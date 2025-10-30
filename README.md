# E-commerce Inventory & Demand Forecasting - Observability Project

A comprehensive observability mini-project that demonstrates real-time inventory monitoring, order rate analysis, stockout prediction, and demand forecasting using **Prometheus** and **ELK Stack** (Elasticsearch & Kibana).

## Project Overview

This project simulates an e-commerce inventory management system with:
- **5 Products**: LAPTOP-001, PHONE-002, HEADPHONES-003, MOUSE-004, KEYBOARD-005
- **3 Warehouses**: WH-NYC (New York), WH-LDN (London), WH-TYO (Tokyo)
- **Real-time Metrics**: Inventory levels, order rates, stockout predictions, demand forecasts
- **Auto-reorder Alerts**: Automatic reorder recommendations when inventory is predicted to run out
- **ML-based Forecasting**: Linear regression for 7-day demand forecasting and stockout prediction

## Features

✅ **Prometheus Metrics**: Real-time inventory, orders, forecasts, and predictions  
✅ **ELK Stack Integration**: JSON logs shipped to Elasticsearch via Filebeat  
✅ **Metricbeat Integration**: Prometheus metrics federated to Elasticsearch  
✅ **Kibana Dashboards**: Visualize inventory trends, order patterns, and forecasts  
✅ **Machine Learning**: Linear regression for demand forecasting and stockout prediction  
✅ **Auto-alerts**: Reorder recommendations when stockout is predicted within 24 hours  

## Architecture

```
┌─────────────┐
│   App       │─── Generates inventory & order data
│  (Python)   │─── Exposes /metrics endpoint
└──────┬──────┘
       │
       ├───> Prometheus (Scrapes /metrics)
       │
       ├───> Filebeat (Ships JSON logs to Elasticsearch)
       │
       └───> Metricbeat (Federates Prometheus metrics to Elasticsearch)
              │
              ▼
       ┌──────────────┐
       │ Elasticsearch│
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │    Kibana    │─── Visualization & Dashboards
       └──────────────┘
```

## Metrics Generated

### Prometheus Metrics

- `inventory_level_units{product_id, warehouse_id}` - Current inventory in units
- `orders_per_minute{product_id}` - Order rate per product
- `predicted_stockout_hours{product_id, warehouse_id}` - Hours until stockout (regression-based)
- `demand_forecast_units{product_id}` - 7-day ahead demand forecast
- `orders_total{product_id}` - Total orders placed (counter)
- `reorder_events_total{product_id, warehouse_id}` - Reorder alerts triggered (counter)
- `processing_latency_seconds` - Event processing latency (histogram)

## Prerequisites

- **Docker Desktop** installed and running (with WSL2 backend on Windows)
- **Ports available**: 9200 (Elasticsearch), 5601 (Kibana), 9090 (Prometheus), 8000 (App)
- **Minimum 4GB RAM** recommended

## Quick Start

### 1. Clone/Download Project

```powershell
cd "D:\PROJECTS\ELK  Stack"
```

### 2. Start the Stack

```powershell
docker compose up -d --build
```

This will start:
- **Elasticsearch** (port 9200)
- **Kibana** (port 5601)
- **Prometheus** (port 9090)
- **Metricbeat** (Prometheus → Elasticsearch)
- **Filebeat** (App logs → Elasticsearch)
- **E-commerce App** (port 8000)

### 3. Wait for Services to Start

Wait 30-60 seconds for all services to initialize. Check status:

```powershell
docker ps
```

All containers should show "Up" status.

### 4. Verify Data Generation

Visit the app health endpoint:
- **App**: http://localhost:8000/
- **Metrics**: http://localhost:8000/metrics
- **Health**: http://localhost:8000/health

Check Prometheus:
- **Prometheus UI**: http://localhost:9090
- Try query: `inventory_level_units`

## Setting Up Kibana

### Step 1: Create Data Views

1. Open **Kibana**: http://localhost:5601
2. Go to **Stack Management** → **Data Views**
3. Click **Create data view**

#### Data View 1: Application Logs
- **Name**: `app-logs`
- **Index pattern**: `filebeat-*`
- **Timestamp field**: `@timestamp`
- Click **Create data view**

#### Data View 2: Prometheus Metrics
- **Name**: `prom-metrics`
- **Index pattern**: `metricbeat-*`
- **Timestamp field**: `@timestamp`
- Click **Create data view**

### Step 2: Explore Data in Discover

1. Go to **Discover** (left sidebar)
2. Select **app-logs** data view
3. You should see events with fields:
   - `type` (order, inventory, reorder_alert, restock)
   - `product_id`
   - `warehouse_id`
   - `inventory_units`
   - `predicted_stockout_hours`
   - `orders_per_hour`

4. Try filters:
   - `type: reorder_alert` - See reorder recommendations
   - `type: order` - See order events
   - `low_stock_warning: true` - See low stock alerts

### Step 3: Create Visualizations

#### Visualization 1: Inventory Levels Over Time
1. Go to **Visualize Library** → **Create visualization** → **Lens**
2. Select data view: `app-logs`
3. **X-axis**: `@timestamp` (Date Histogram)
4. **Y-axis**: Average of `inventory_units`
5. **Split by**: `warehouse_id.keyword`
6. **Filter**: `type: inventory`
7. **Title**: "Inventory Levels by Warehouse"
8. Click **Save**

#### Visualization 2: Order Rates by Product
1. Create new **Lens** visualization
2. Select data view: `app-logs`
3. **X-axis**: `@timestamp`
4. **Y-axis**: Average of `orders_per_hour`
5. **Split by**: `product_id.keyword`
6. **Filter**: `type: inventory`
7. **Title**: "Order Rates by Product"
8. Click **Save**

#### Visualization 3: Stockout Predictions
1. Create new **Lens** visualization
2. Select data view: `app-logs`
3. **X-axis**: `@timestamp`
4. **Y-axis**: Average of `predicted_stockout_hours`
5. **Split by**: `product_id.keyword`
6. **Color by**: `warehouse_id.keyword`
7. **Filter**: `type: inventory`
8. **Title**: "Predicted Stockout Hours"
9. Click **Save**

#### Visualization 4: Reorder Alerts
1. Create new **Lens** visualization
2. Select data view: `app-logs`
3. **Chart type**: **Bar chart**
4. **X-axis**: `product_id.keyword`
5. **Y-axis**: Count of documents
6. **Filter**: `type: reorder_alert`
7. **Title**: "Reorder Alerts by Product"
8. Click **Save**

#### Visualization 5: Demand Forecast (from Metrics)
1. Create new **Lens** visualization
2. Select data view: `prom-metrics`
3. **X-axis**: `@timestamp`
4. **Y-axis**: Average of `prometheus.demand_forecast_units`
5. **Split by**: `prometheus.labels.product_id`
6. **Title**: "7-Day Demand Forecast"
7. Click **Save**

#### Visualization 6: Inventory Metrics (Prometheus)
1. Create new **Lens** visualization
2. Select data view: `prom-metrics`
3. **X-axis**: `@timestamp`
4. **Y-axis**: Average of `prometheus.inventory_level_units`
5. **Split by**: `prometheus.labels.product_id`
6. **Color by**: `prometheus.labels.warehouse_id`
7. **Title**: "Inventory Levels (Prometheus Metrics)"
8. Click **Save**

### Step 4: Create Dashboard

1. Go to **Dashboards** → **Create dashboard**
2. Click **Add panels**
3. Add all 6 visualizations created above
4. Arrange panels as desired
5. **Title**: "   "
6. Click **Save**

## Prometheus Queries

Try these queries in Prometheus UI (http://localhost:9090):

### Basic Queries

```promql
# Current inventory levels
inventory_level_units

# Inventory for specific product
inventory_level_units{product_id="PHONE-002"}

# Order rates
orders_per_minute

# Stockout predictions (when less than 24 hours)
predicted_stockout_hours < 24

# Demand forecasts
demand_forecast_units
```

### Advanced Queries

```promql
# Total orders across all products
sum(rate(orders_total[5m])) by (product_id)

# Average inventory across warehouses per product
avg(inventory_level_units) by (product_id)

# Products at risk of stockout
predicted_stockout_hours < 24 and predicted_stockout_hours > 0

# Reorder events rate
rate(reorder_events_total[5m]) by (product_id, warehouse_id)
```

## Project Structure

```
ELK Stack/
├── app/
│   ├── main.py              # E-commerce simulator application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Docker image definition
├── prometheus/
│   └── prometheus.yml      # Prometheus configuration
├── beats/
│   ├── metricbeat.yml      # Metricbeat configuration
│   └── filebeat.yml        # Filebeat configuration
├── docker-compose.yml      # Docker Compose orchestration
└── README.md              # This file
```

## Event Types in Logs

The application generates these event types:

1. **`order`**: Order fulfillment events
   - Fields: `product_id`, `warehouse_id`, `quantity`, `remaining_inventory`

2. **`inventory`**: Periodic inventory status
   - Fields: `product_id`, `warehouse_id`, `inventory_units`, `orders_per_hour`, `predicted_stockout_hours`, `low_stock_warning`

3. **`reorder_alert`**: Automatic reorder recommendations
   - Fields: `product_id`, `warehouse_id`, `current_inventory`, `predicted_stockout_hours`, `recommended_reorder_quantity`

4. **`restock`**: Inventory restocking events
   - Fields: `product_id`, `warehouse_id`, `restocked_quantity`, `new_inventory`

## Troubleshooting

### Data Not Appearing in Kibana

1. **Check if Elasticsearch has indices**:
   - Kibana Dev Tools → Run: `GET _cat/indices?v`
   - Should see `filebeat-*` and `metricbeat-*` indices

2. **Verify app is generating data**:
   ```powershell
   docker logs -f data-app
   ```

3. **Check Filebeat**:
   ```powershell
   docker logs filebeat
   ```

4. **Check Metricbeat**:
   ```powershell
   docker logs metricbeat
   ```

### Services Not Starting

```powershell
# Restart all services
docker compose restart

# Rebuild and restart
docker compose up -d --build --force-recreate
```

### Clear All Data and Start Fresh

```powershell
docker compose down -v
docker compose up -d --build
```

## Learning Outcomes

After completing this project, you will understand:

✅ **Time Series Analytics**: Collecting and analyzing inventory and order metrics  
✅ **Prometheus Integration**: Scraping metrics and querying with PromQL  
✅ **ELK Stack Deployment**: Data ingestion, storage, and visualization  
✅ **Machine Learning Application**: Regression for forecasting and prediction  
✅ **Real-world Observability**: End-to-end monitoring and alerting workflows  
✅ **Data Visualization**: Creating dashboards for operational insights  

## Cleanup

To stop and remove everything:

```powershell
docker compose down -v
```

This removes all containers and volumes (including Elasticsearch data).

## License

This is an educational project for workshop purposes.

---

**Happy Observing! 📊🛒📈**

