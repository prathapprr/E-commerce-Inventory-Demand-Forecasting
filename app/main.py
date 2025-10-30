import os
import json
import time
import threading
from datetime import datetime
from typing import List
import numpy as np
from fastapi import FastAPI
from prometheus_client import Gauge, Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

LOG_DIR = os.getenv("LOG_DIR", "/var/log/app")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "events.jsonl")

registry = CollectorRegistry()

inventory_level_units = Gauge(
    "inventory_level_units",
    "Current inventory level in units",
    ["product_id", "warehouse_id"],
    registry=registry,
)
orders_per_minute = Gauge(
    "orders_per_minute",
    "Order rate per minute for product",
    ["product_id"],
    registry=registry,
)
predicted_stockout_hours = Gauge(
    "predicted_stockout_hours",
    "Predicted hours until stockout using regression analysis",
    ["product_id", "warehouse_id"],
    registry=registry,
)
demand_forecast_units = Gauge(
    "demand_forecast_units",
    "7-day ahead demand forecast in units",
    ["product_id"],
    registry=registry,
)
orders_total = Counter(
    "orders_total",
    "Total number of orders placed",
    ["product_id"],
    registry=registry,
)
reorder_events_total = Counter(
    "reorder_events_total",
    "Number of reorder alerts triggered",
    ["product_id", "warehouse_id"],
    registry=registry,
)
processing_latency_seconds = Histogram(
    "processing_latency_seconds",
    "Order processing latency",
    registry=registry,
)

app = FastAPI(title="Observability Mini Project: E-commerce Inventory & Demand Forecasting")

def write_event(event: dict) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def linear_regression_predict(x_values: List[float], y_values: List[float], future_x: float) -> float:
    if len(x_values) < 3:
        return y_values[-1] if y_values else 0.0
    x = np.array(x_values)
    y = np.array(y_values)
    x_mean = x.mean()
    y_mean = y.mean()
    cov = ((x - x_mean) * (y - y_mean)).sum()
    var = ((x - x_mean) ** 2).sum()
    if var == 0:
        return y_mean
    slope = cov / var
    intercept = y_mean - slope * x_mean
    return float(intercept + slope * future_x)

def predict_stockout_hours(inventory: float, consumption_rate_per_hour: float) -> float:
    if consumption_rate_per_hour <= 0:
        return 9999.0
    return max(0.0, inventory / consumption_rate_per_hour) if inventory > 0 else 0.0

def generate_ecommerce_data(step_seconds: int = 5) -> None:
    products = ["LAPTOP-001", "PHONE-002", "HEADPHONES-003", "MOUSE-004", "KEYBOARD-005"]
    warehouses = ["WH-NYC", "WH-LDN", "WH-TYO"]
    inventory = {(p, w): np.random.randint(50, 500) for p in products for w in warehouses}
    order_history = {p: [] for p in products}
    inventory_history = {(p, w): [] for p in products for w in warehouses}
    demand_history = {p: [] for p in products}
    forecast_cache = {p: 0.0 for p in products}
    window_size = 60
    time_window = []
    base_demand = {
        "LAPTOP-001": 0.8,
        "PHONE-002": 1.2,
        "HEADPHONES-003": 0.6,
        "MOUSE-004": 0.4,
        "KEYBOARD-005": 0.3,
    }
    while True:
        start_t = time.perf_counter()
        now = datetime.utcnow().isoformat()
        current_minute = int(time.time() / 60)
        time_window.append(current_minute)
        if len(time_window) > window_size:
            time_window.pop(0)
        hour_of_day = datetime.now().hour
        diurnal_factor = 0.5 + 0.5 * np.sin((hour_of_day - 6) * np.pi / 12) if 6 <= hour_of_day <= 22 else 0.2
        seasonal_factor = 1.0 + 0.3 * np.sin(time.time() / 86400.0)
        for product_id in products:
            order_rate = base_demand[product_id] * diurnal_factor * seasonal_factor
            orders_this_minute = max(0, int(np.random.poisson(order_rate)))
            order_history[product_id].append({
                "timestamp": current_minute,
                "orders": orders_this_minute
            })
            if len(order_history[product_id]) > 168:
                order_history[product_id].pop(0)
            recent_orders = [o["orders"] for o in order_history[product_id][-12:]]
            avg_orders_per_min = float(np.mean(recent_orders)) if recent_orders else order_rate
            orders_per_minute.labels(product_id=product_id).set(avg_orders_per_min)
            total_inv = sum(inventory[(product_id, w)] for w in warehouses)
            if total_inv > 0 and orders_this_minute > 0:
                for warehouse_id in warehouses:
                    inv_ratio = inventory[(product_id, warehouse_id)] / total_inv
                    orders_to_fulfill = min(
                        inventory[(product_id, warehouse_id)],
                        max(1, int(orders_this_minute * inv_ratio))
                    )
                    if orders_to_fulfill > 0:
                        inventory[(product_id, warehouse_id)] -= orders_to_fulfill
                        orders_total.labels(product_id=product_id).inc(orders_to_fulfill)
                        write_event({
                            "ts": now,
                            "type": "order",
                            "product_id": product_id,
                            "warehouse_id": warehouse_id,
                            "quantity": orders_to_fulfill,
                            "remaining_inventory": inventory[(product_id, warehouse_id)],
                        })
            if len(order_history[product_id]) >= 7:
                recent_demand = [sum([o["orders"] for o in order_history[product_id][i*24:(i+1)*24]], 0)
                                 if i*24 < len(order_history[product_id]) else 0
                                 for i in range(min(7, len(order_history[product_id]) // 24 + 1))]
                if len(recent_demand) >= 3:
                    x_days = list(range(len(recent_demand)))
                    forecast_day = len(recent_demand)
                    forecast_units = linear_regression_predict(x_days, recent_demand, forecast_day) * 24 * 60
                    forecast_units = max(0, forecast_units)
                    forecast_cache[product_id] = forecast_units
                    demand_forecast_units.labels(product_id=product_id).set(forecast_units)
            for warehouse_id in warehouses:
                current_inv = inventory[(product_id, warehouse_id)]
                inventory_history[(product_id, warehouse_id)].append(current_inv)
                if len(inventory_history[(product_id, warehouse_id)]) > window_size:
                    inventory_history[(product_id, warehouse_id)].pop(0)
                inventory_level_units.labels(product_id=product_id, warehouse_id=warehouse_id).set(current_inv)
                recent_orders_for_product = [o["orders"] for o in order_history[product_id][-12:]]
                orders_per_hour = float(np.sum(recent_orders_for_product)) * 60 if recent_orders_for_product else 0.1
                if len(inventory_history[(product_id, warehouse_id)]) >= 5:
                    inv_series = inventory_history[(product_id, warehouse_id)][-20:]
                    x_time = list(range(len(inv_series)))
                    if inv_series[-1] > 0:
                        projected_stockout = linear_regression_predict(
                            x_time, inv_series,
                            len(inv_series) + (inv_series[-1] / max(0.1, orders_per_hour / 60))
                        )
                        stockout_hours = predict_stockout_hours(current_inv, orders_per_hour)
                        if len(inv_series) >= 3:
                            slope = (inv_series[-1] - inv_series[0]) / max(1, len(inv_series) - 1)
                            if slope < 0:
                                stockout_hours = abs(current_inv / max(0.1, abs(slope) * 12))
                            else:
                                stockout_hours = 999.0
                    else:
                        stockout_hours = 0.0
                else:
                    stockout_hours = predict_stockout_hours(current_inv, orders_per_hour)
                predicted_stockout_hours.labels(product_id=product_id, warehouse_id=warehouse_id).set(stockout_hours)
                reorder_threshold_hours = 24.0
                if stockout_hours > 0 and stockout_hours < reorder_threshold_hours and current_inv > 0:
                    reorder_quantity = int(forecast_cache[product_id] / len(warehouses)) if forecast_cache[product_id] > 0 else 100
                    if reorder_quantity > 0:
                        reorder_events_total.labels(product_id=product_id, warehouse_id=warehouse_id).inc()
                        write_event({
                            "ts": now,
                            "type": "reorder_alert",
                            "product_id": product_id,
                            "warehouse_id": warehouse_id,
                            "current_inventory": current_inv,
                            "predicted_stockout_hours": round(stockout_hours, 2),
                            "recommended_reorder_quantity": reorder_quantity,
                        })
                if np.random.rand() < 0.01:
                    restock_amount = np.random.randint(50, 200)
                    inventory[(product_id, warehouse_id)] += restock_amount
                    write_event({
                        "ts": now,
                        "type": "restock",
                        "product_id": product_id,
                        "warehouse_id": warehouse_id,
                        "restocked_quantity": restock_amount,
                        "new_inventory": inventory[(product_id, warehouse_id)],
                    })
                write_event({
                    "ts": now,
                    "type": "inventory",
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "inventory_units": current_inv,
                    "orders_per_hour": round(orders_per_hour, 2),
                    "predicted_stockout_hours": round(stockout_hours, 2),
                    "low_stock_warning": current_inv < 50,
                })
        processing_latency_seconds.observe(time.perf_counter() - start_t)
        time.sleep(step_seconds)

@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def root():
    return {
        "service": "ecommerce-inventory-forecasting",
        "description": "Real-time E-commerce Inventory & Demand Forecasting System",
        "metrics": "/metrics",
        "log_path": LOG_PATH,
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

def _start_background_threads():
    threading.Thread(target=generate_ecommerce_data, daemon=True).start()

_start_background_threads()
