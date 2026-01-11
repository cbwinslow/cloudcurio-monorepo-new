# Sponsorship & Tour Management Toolsets

This document provides detailed documentation for sponsorship and tour management tools.

## Sponsorship Manager Tools

| Tool Name             | Description                                  | Status |
| --------------------- | -------------------------------------------- | ------ |
| `sponsor_research`    | Research and identify potential sponsors     | Active |
| `create_sponsor_read` | Generate personalized sponsor advertisements | Active |
| `track_performance`   | Monitor sponsor campaign performance         | Active |
| `generate_report`     | Create performance reports for sponsors      | Active |

---

## sponsor_research

Researches and identifies potential sponsors based on target demographics and budget.

### Parameters

| Parameter             | Type   | Required | Description                  |
| --------------------- | ------ | -------- | ---------------------------- |
| `target_demographics` | array  | Yes      | Target audience demographics |
| `budget_range`        | object | Yes      | Budget constraints           |
| `excluded_categories` | array  | No       | Categories to exclude        |

### Example Usage

```json
{
  "target_demographics": ["18-34", "comedy fans", "urban"],
  "budget_range": { "min": 5000, "max": 50000 },
  "excluded_categories": ["alcohol", "gambling"]
}
```

---

## create_sponsor_read

Generates personalized sponsor advertisements based on sponsor information.

### Parameters

| Parameter           | Type   | Required | Description                      |
| ------------------- | ------ | -------- | -------------------------------- |
| `sponsor_info`      | object | Yes      | Sponsor details and requirements |
| `integration_style` | enum   | Yes      | Style of sponsor integration     |
| `duration`          | number | Yes      | Target duration in seconds       |

### Integration Styles

- `host_read` - Host reads ad naturally during episode
- `produced_ad` - Pre-produced advertisement
- `product_demo` - Live product demonstration

### Example Usage

```json
{
  "sponsor_info": {
    "name": "Squarespace",
    "offer": "Get 10% off",
    "coupon": "PODCAST10",
    "key_points": ["Easy to use", "Professional templates"]
  },
  "integration_style": "host_read",
  "duration": 90
}
```

---

## track_performance

Monitors sponsor campaign performance with specified metrics.

### Parameters

| Parameter     | Type   | Required | Description              |
| ------------- | ------ | -------- | ------------------------ |
| `campaign_id` | string | Yes      | Campaign identifier      |
| `metrics`     | array  | Yes      | Metrics to track         |
| `time_period` | string | Yes      | Time period for analysis |

### Example Usage

```json
{
  "campaign_id": "squarespace_2024_q1",
  "metrics": ["impressions", "clicks", "conversions", "brand_lift"],
  "time_period": "last_30_days"
}
```

---

## generate_report

Creates performance reports for sponsors with demographic data.

### Parameters

| Parameter              | Type    | Required | Description                   |
| ---------------------- | ------- | -------- | ----------------------------- |
| `sponsor_id`           | string  | Yes      | Sponsor identifier            |
| `report_period`        | string  | Yes      | Report time period            |
| `include_demographics` | boolean | No       | Include audience demographics |

### Example Usage

```json
{
  "sponsor_id": "squarespace",
  "report_period": "Q1_2024",
  "include_demographics": true
}
```

---

## Tour Manager Tools

| Tool Name              | Description                                | Status |
| ---------------------- | ------------------------------------------ | ------ |
| `venue_research`       | Research and identify suitable venues      | Active |
| `create_tour_schedule` | Generate and manage tour itinerary         | Active |
| `manage_tickets`       | Handle ticket sales and inventory          | Active |
| `promote_event`        | Create promotional materials and campaigns | Active |

---

## venue_research

Researches venues based on location, capacity, and technical requirements.

### Parameters

| Parameter                | Type   | Required | Description                  |
| ------------------------ | ------ | -------- | ---------------------------- |
| `city`                   | string | Yes      | Target city                  |
| `capacity_range`         | object | Yes      | Minimum and maximum capacity |
| `budget_constraints`     | number | Yes      | Budget limit                 |
| `technical_requirements` | array  | Yes      | Technical needs              |

### Example Usage

```json
{
  "city": "Chicago",
  "capacity_range": { "min": 1000, "max": 5000 },
  "budget_constraints": 25000,
  "technical_requirements": ["av_system", "green_room", "load_in_access"]
}
```

---

## create_tour_schedule

Generates a complete tour itinerary with dates and locations.

### Parameters

| Parameter     | Type   | Required | Description     |
| ------------- | ------ | -------- | --------------- |
| `start_date`  | string | Yes      | Tour start date |
| `end_date`    | string | Yes      | Tour end date   |
| `cities`      | array  | Yes      | List of cities  |
| `event_types` | array  | Yes      | Types of events |

### Example Usage

```json
{
  "start_date": "2024-03-01",
  "end_date": "2024-03-31",
  "cities": ["New York", "Chicago", "Los Angeles", "Seattle"],
  "event_types": ["live_podcast", "meet_greet"]
}
```

---

## manage_tickets

Handles ticket sales, pricing tiers, and inventory management.

### Parameters

| Parameter        | Type   | Required | Description                |
| ---------------- | ------ | -------- | -------------------------- |
| `event_id`       | string | Yes      | Event identifier           |
| `ticket_types`   | array  | Yes      | Types of tickets available |
| `pricing_tiers`  | object | Yes      | Pricing structure          |
| `sales_platform` | string | Yes      | Ticket sales platform      |

### Example Usage

```json
{
  "event_id": "nyc_live_0315",
  "ticket_types": ["general", "vip", "meet_greet"],
  "pricing_tiers": {
    "general": 50,
    "vip": 150,
    "meet_greet": 250
  },
  "sales_platform": "eventbrite"
}
```

---

## promote_event

Creates promotional content and campaigns for live events.

### Parameters

| Parameter            | Type   | Required | Description              |
| -------------------- | ------ | -------- | ------------------------ |
| `event_details`      | object | Yes      | Event information        |
| `promotion_channels` | array  | Yes      | Channels for promotion   |
| `budget`             | number | Yes      | Promotion budget         |
| `target_audience`    | array  | Yes      | Target audience segments |

### Example Usage

```json
{
  "event_details": {
    "name": "Live Podcast Recording",
    "date": "2024-03-15",
    "venue": "Madison Square Garden"
  },
  "promotion_channels": ["social", "email", "radio"],
  "budget": 5000,
  "target_audience": ["podcast_listeners", "comedy_fans"]
}
```

---

## Workflow Integration

### Sponsorship Workflow

```
sponsor_research → create_sponsor_read → track_performance → generate_report
```

### Tour Management Workflow

```
venue_research → create_tour_schedule → manage_tickets → promote_event
```

---

## Best Practices

1. **Research thoroughly** - Vet sponsors for audience alignment
2. **Create natural integrations** - Host reads perform best
3. **Track everything** - Detailed analytics build trust
4. **Plan logistics early** - Book venues well in advance
5. **Promote consistently** - Multi-channel promotion drives ticket sales
