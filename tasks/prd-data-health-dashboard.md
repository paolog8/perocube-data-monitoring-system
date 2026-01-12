# PRD: Data Health Dashboard

## 1. Introduction/Overview

This document outlines the requirements for a Grafana dashboard focused on monitoring the health of the Perocube data collection system. The primary goal is to provide at-a-glance visibility into the status of data ingestion, identify data gaps, and alert stakeholders to potential issues. This will help ensure data integrity and reliability for both scientists and system administrators.

## 2. Goals

- Provide a centralized dashboard to monitor the health of all connected sensors and devices.
- Quickly identify sensors that are offline or not transmitting data as expected.
- Quantify data completeness by highlighting gaps in data collection.
- Offer insights into the volume of data being collected over time.
- Enable proactive alerting for data collection failures.

## 3. User Stories

### US-001: Create database views for dashboard queries
**Description:** As a developer, I need to create performant database views or functions to aggregate data for the Grafana dashboard panels so that the dashboard loads quickly and efficiently.

**Acceptance Criteria:**
- [ ] Create a SQL view/function to calculate the last seen timestamp for each sensor.
- [ ] Create a SQL view/function to count the number of measurements per sensor, per day and per week.
- [ ] Create a SQL view/function to identify data gaps longer than a configurable threshold (defaulting to 5 minutes).
- [ ] Ensure all new database objects are included in a new Flyway migration script.
- [ ] All queries execute in under 5 seconds for a dataset spanning 30 days.
- [ ] Typecheck/lint passes.

### US-002: Provision a new Grafana dashboard
**Description:** As a system administrator, I want a new "Data Health" dashboard to be automatically provisioned in Grafana so that I can immediately start monitoring the system.

**Acceptance Criteria:**
- [ ] A new JSON file `grafana/provisioning/dashboards/data_health.json` is created.
- [ ] A corresponding `dashboard.yaml` entry is added to `grafana/provisioning/dashboards/` to provision the new dashboard.
- [ ] The dashboard has a title "Data Collection Health".
- [ ] The dashboard includes variables for selecting device, sensor, and time range.

### US-003: Display the last seen timestamp for each sensor
**Description:** As a user, I want to see the last time each sensor sent data so that I can quickly identify if a sensor has stopped reporting.

**Acceptance Criteria:**
- [ ] A "Last Seen" panel is added to the dashboard.
- [ ] The panel is a table that lists each sensor/device.
- [ ] The table shows the timestamp of the very last data point received for that sensor.
- [ ] The timestamp is displayed in a human-readable format (e.g., "YYYY-MM-DD HH:mm:ss").
- [ ] The table is sorted by the last seen timestamp in ascending order (oldest first).
- [ ] Verify visually in browser.

### US-004: Visualize the number of measurements over time
**Description:** As a user, I want to see the number of measurements per day and per week so that I can understand data volume and spot significant drops.

**Acceptance Criteria:**
- [ ] A "Measurement Count" panel is added to the dashboard.
- [ ] The panel is a bar chart showing the total number of measurements.
- [ ] A dropdown or toggle allows switching the view between "per day" and "per week".
- [ ] The x-axis represents time, and the y-axis represents the count of measurements.
- [ ] The panel can be filtered by device/sensor.
- [ ] Verify visually in browser.

### US-005: Visualize data collection frequency
**Description:** As a user, I want to compare the actual data collection frequency against an expected frequency so that I can identify if sensors are reporting data less often than they should.

**Acceptance Criteria:**
- [ ] A "Collection Frequency" panel is added to the dashboard.
- [ ] The panel displays the average time between consecutive measurements for each sensor over the selected time range.
- [ ] The panel includes a configurable "Expected Frequency" threshold (e.g., a line on the graph).
- [ ] Sensors reporting less frequently than the threshold are highlighted.
- [ ] Verify visually in browser.

### US-006: Identify and visualize missing data gaps
**Description:** As a user, I want to see periods where data is missing for longer than a specified threshold so that I can assess the completeness of the data.

**Acceptance Criteria:**
- [ ] A "Data Gaps (>5 min)" panel is added to the dashboard.
- [ ] The panel uses a timeline or gantt chart visualization to show gaps for each sensor.
- [ ] Only gaps longer than 5 minutes are displayed.
- [ ] The visualization clearly shows the start and end time of each gap.
- [ ] The panel can be filtered by device/sensor.
- [ ] Verify visually in browser.

## 4. Functional Requirements

- **FR-1:** The dashboard shall be accessible to all users with Grafana access.
- **FR-2:** The dashboard must load in under 10 seconds.
- **FR-3:** All panels must be filterable by `device_id` and `sensor_id`.
- **FR-4:** A time range filter shall be present at the top of the dashboard.
- **FR-5:** The "Data Gaps" panel will use a fixed threshold of 5 minutes to define a gap.
- **FR-6:** The "Measurement Count" panel will provide options to view data aggregated by day or by week.
- **FR-7:** The "Last Seen" panel will color-code timestamps: red if > 1 hour ago, orange if > 15 minutes ago, green otherwise.

## 5. Non-Goals (Out of Scope)

- Automatic email or Slack alerting from this dashboard in this iteration. (Alerting rules can be added later).
- A UI for configuring the "expected frequency" or "gap threshold" for each sensor. These will be set to sensible defaults in the dashboard queries for now.
- Historical backfilling of missing data. This dashboard is for monitoring and visualization only.
- Any changes to the data ingestion logic itself.

## 6. Design Considerations

- The dashboard should follow a logical layout, with the most critical information at the top (e.g., "Last Seen").
- Use consistent color-coding across panels to indicate status (e.g., red for problems, green for healthy).
- Leverage Grafana's built-in table, bar chart, and time-series panels. A timeline/gantt-style panel might require a plugin.

## 7. Technical Considerations

- The queries powering the dashboard must be optimized for performance to avoid overloading the TimescaleDB database. This may involve creating materialized views or rollups.
- The "expected frequency" is not currently known or stored. For the initial version, we will need to use a reasonable, configurable default in the Grafana panel. This highlights the need for a future feature to store sensor-specific metadata.
- Grafana dashboard provisioning will be handled by placing the dashboard JSON in the `grafana/provisioning/dashboards` directory.

## 8. Success Metrics

- Time to identify an offline sensor is reduced from hours/days to minutes.
- Scientists and admins can confidently assess data completeness for any given day within 5 minutes of viewing the dashboard.
- A 75% reduction in manual queries needed to check data collection status.

## 9. Open Questions

- What is the expected data collection frequency for different sensor types? This information is needed to accurately implement US-005. A configurable default will be used for now.
- What Grafana plugins are available and approved for use in our environment for visualizations like a timeline/gantt chart?
