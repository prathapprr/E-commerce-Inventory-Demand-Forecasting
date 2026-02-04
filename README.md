# E-commerce Inventory & Demand Forecasting

![Elasticsearch](https://img.shields.io/badge/Elasticsearch-7.17-blue?logo=elasticsearch) ![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-orange?logo=prometheus) ![Kibana](https://img.shields.io/badge/Kibana-Dashboards-005571?logo=kibana) ![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

A **demo-ready, open-source observability project** for real-time inventory monitoring, order rate analytics, stockout prediction, and demand forecasting. Built on **Prometheus** (for metrics) and the **ELK Stack** (Elasticsearch, Logstash/Beats, Kibana) for log management and data visualization.
localhost
---

## Overview

Monitor, analyze, and act on e-commerce inventory signals from three warehouses and five products—all in real time—using modern observability stacks. Visualize data in interactive dashboards, forecast demand with linear regression, and get actionable reorder alerts automatically.

---

## Technologies Used
- **Prometheus** – Scrapes real-time inventory, order, and forecast metrics from a Python backend
- **Elasticsearch** – Indexes logs & metrics for search and analytics
- **Kibana** – Data discovery, dashboards, and visualization
- **Filebeat/Metricbeat** – Ship logs and federate Prometheus metrics into Elastic
- **Docker Compose** – Single command stack boot-up

---

## Features
- **Live Inventory Tracking:** Product/warehouse breakdown
- **Order & Demand Analytics:** View order rates and predictions
- **Forecast & ML:** Linear regression for demand & stockout time
- **Reorder Alerts:** Automated alerting for low/critical stock
- **Plug-and-Play Visualizations:** Kibana dashboards and Prometheus charts
- **Fully Scripted Demo:** Quick start for learning or demonstration

---

## Project Architecture

![Architecture Diagram](.github/images/architecture.png)

### Data Flow Summary

| Source | Destination | Data Type |
|--------|-------------|-----------|
| App `/metrics` | Prometheus | Gauges, Counters, Histograms |
| App `events.jsonl` | Filebeat → Elasticsearch | Order, Inventory, Alert logs |
| Prometheus | Metricbeat → Elasticsearch | Federated metrics |
| Elasticsearch | Kibana | Dashboards & Visualizations |

---

## Example Metrics
- `inventory_level_units{product_id, warehouse_id}` – Live inventory
- `orders_per_minute{product_id}` – Order rate
- `predicted_stockout_hours{product_id, warehouse_id}` – ML: time to stockout
- `demand_forecast_units{product_id}` – ML: demand forecast
- `reorder_events_total{product_id, warehouse_id}` – Auto-reorder events

---

## Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- WSL2 backend (if on Windows)
- Open ports: 9200 (Elasticsearch), 5601 (Kibana), 9090 (Prometheus), 8000 (App)

### 2. Clone & Launch
```powershell
git clone <your-repo-url>
cd "ELK  Stack"
docker compose up -d --build
```
Stack will launch:
- **Elasticsearch**: http://localhost:9200
- **Kibana Dashboard**: http://localhost:5601
- **Prometheus UI**: http://localhost:9090
- **App (API & metrics)**: http://localhost:8000

### 3. Verify
- Visit `/metrics` at `http://localhost:8000/metrics`
- Check dashboards in Kibana and Prometheus
- See events/logs in Kibana Discover (type: inventory/order/reorder_alert/restock)

---

## Data Model (Event Types)
- **order:**  product_id, warehouse_id, quantity, remaining_inventory
- **inventory:** periodic stock status, demand, prediction fields
- **reorder_alert:** generated on forecasted shortage
- **restock:** logs inventory replenishment

---

## Dashboards & Visualizations
Build the following in Kibana:
- **Inventory by Warehouse**: Line chart of units per site over time
- **Order Rates by Product**: Time-chart by product
- **Stockout Predictions**: Visual forecast for low inventory
- **Reorder Alerts**: Bar chart for which product is generating the most alerts
- **Demand Forecast**: 7-day predicted demand (from Prometheus data)

---

## Learning Outcomes
- Observability for business metrics (not just infrastructure)
- Real-world data flows: From API ⟶ metrics & logs ⟶ dashboards
- Deploying & integrating Prometheus + ELK
- Building actionable, interactive e-commerce analytics
- Simple ML for supply chain insight

---

## Troubleshooting / Tips
- Log in to services (`docker ps`, `docker logs <container>`) for troubleshooting
- Check Elasticsearch indices: Kibana > Dev Tools > `GET _cat/indices?v`
- Restart all with:      `docker compose restart`
- Reset/clear volumes:   `docker compose down -v`

---

**Happy Observing!**
