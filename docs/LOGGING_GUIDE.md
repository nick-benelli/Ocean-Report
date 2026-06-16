# Ocean Report - Logging Guide

## Overview
Comprehensive logging has been added throughout the application to help track down latency issues and understand the timing of each operation.

## Log Structure

### Main Workflow Stages
The workflow is divided into 5 main steps:

```
================================================================================
Starting Ocean Report Email Process...
Today is Sunday, June 15, 2026
Run mode: PRODUCTION | Send email: True
================================================================================

[STEP 1/5] Loading configuration...
Configuration loaded in 0.05 seconds

[STEP 2/5] Fetching email recipients...
  → Fetching recipients from URL (test=False)
  → Fetching recipients from Gist: https://gist.githubusercontent.com/...
  ✓ Recipients fetched from Gist in 0.23 seconds
  ✓ Recipients fetched from URL in 0.24 seconds
Recipients fetched in 0.24 seconds (found 15 recipients)

[STEP 3/5] Fetching weather data from APIs...
  → Fetching tide data from NOAA...
    → Making NOAA API request for tides (station: 8534720, date: 20260615)
    ✓ NOAA Tides API responded in 0.45 seconds. Found 4 predictions.
  ✓ Tide data fetched in 0.46 seconds (4 events)
  
  → Fetching water temperature from NOAA...
    → Making NOAA API request for water temperature (station: 8534720)
    ✓ NOAA Water Temperature API responded in 0.38 seconds. Found 1 records.
  ✓ Water temperature fetched in 0.39 seconds (72.5°F)
  
  → Fetching wind forecast from Open-Meteo...
    → Making Open-Meteo API request for wind forecast (lat: 39.6542, lon: -74.1084)
    ✓ Open-Meteo Wind Forecast API responded in 0.52 seconds. Found 168 hourly records.
  ✓ Wind forecast fetched in 0.53 seconds (4 time slots)
All data fetched successfully in 1.38 seconds

[STEP 4/5] Formatting email content...
Email formatted in 0.01 seconds (body length: 856 chars)

[STEP 5/5] Sending email...
  → Validating email configuration...
  ✓ Email configuration validated
  → Connecting to SMTP and sending to 15 recipients...
  → Sender: your-email@gmail.com
  → Connecting to SMTP server: smtp.gmail.com:587
  ✓ SMTP connection established in 0.34 seconds
  → Starting TLS upgrade...
  ✓ TLS upgrade completed in 0.18 seconds
  → Authenticating with SMTP server...
  ✓ SMTP authentication succeeded in 0.45 seconds
  → Sending email message...
  ✓ Email message sent in 0.23 seconds
  ✓ Email sent successfully!
  ✓ SMTP operations took 1.20 seconds total
  ✓ Complete email operation took 1.21 seconds
Email sent completed in 1.21 seconds

================================================================================
Ocean Report workflow completed successfully!
Total execution time: 2.89 seconds (0.0 minutes)
================================================================================
```

## Key Timing Metrics to Watch

### 1. **Configuration Loading** (Step 1)
- **Normal**: < 0.1 seconds
- **Slow**: > 0.5 seconds
- If slow, check file system performance

### 2. **Recipient Fetching** (Step 2)
- **Normal**: 0.1 - 0.5 seconds
- **Slow**: > 1.0 seconds
- If slow, check:
  - GitHub Gist availability
  - Network connection
  - DNS resolution

### 3. **API Data Fetching** (Step 3)
This is where most delays typically occur:

#### NOAA Tides API
- **Normal**: 0.3 - 0.8 seconds
- **Slow**: > 1.5 seconds

#### NOAA Water Temperature API
- **Normal**: 0.2 - 0.6 seconds
- **Slow**: > 1.2 seconds

#### Open-Meteo Wind API
- **Normal**: 0.3 - 1.0 seconds
- **Slow**: > 2.0 seconds

**Total for all APIs:**
- **Normal**: 1.0 - 2.5 seconds
- **Slow**: > 4.0 seconds

If APIs are consistently slow, check:
- NOAA API status
- Open-Meteo API status
- Network latency
- Geographic location (distance from API servers)

### 4. **Email Formatting** (Step 4)
- **Normal**: < 0.05 seconds
- **Slow**: > 0.1 seconds
- This should be nearly instant

### 5. **SMTP Email Sending** (Step 5)
This can vary significantly:

#### SMTP Connection
- **Normal**: 0.2 - 0.5 seconds
- **Slow**: > 1.0 seconds

#### TLS Upgrade
- **Normal**: 0.1 - 0.3 seconds
- **Slow**: > 0.5 seconds

#### Authentication
- **Normal**: 0.2 - 0.6 seconds
- **Slow**: > 1.0 seconds

#### Sending Message
- **Normal**: 0.1 - 0.5 seconds
- **Slow**: > 1.0 seconds (depends on recipient count)

**Total SMTP:**
- **Normal**: 0.6 - 2.0 seconds
- **Slow**: > 3.0 seconds

If SMTP is slow, check:
- Gmail SMTP server status
- Network connection quality
- Email size (number of recipients)
- Authentication credentials

## Total Expected Runtime

**Normal execution**: 2-5 seconds
**Slow execution**: > 8 seconds

## Troubleshooting Common Issues

### Issue: Total time > 10 seconds
**Check**: All API timing logs to see which API is slowest

### Issue: Inconsistent send times
**Check**: 
1. Time between data retrieval and actual sending (Step 3 vs Step 5 timestamps)
2. SMTP authentication time (may vary with Gmail's rate limiting)
3. Network conditions during the run

### Issue: Email arrives at different times
**Check**:
1. The "Data Retrieved" timestamps in the email itself
2. The total workflow execution time in logs
3. Any delays between workflow completion and email receipt (Gmail delivery)

## Log Levels

- **INFO**: Major milestones and timing summaries
- **DEBUG**: Detailed operation steps and sub-timings

To see debug logs, ensure your logger is configured for DEBUG level in your config or environment.

## Next Steps for Debugging

1. Run the report multiple times and compare logs
2. Note which step takes the longest consistently
3. Check external service status if APIs are slow
4. Monitor network conditions during slow runs
5. Compare timestamps in the email with log timestamps
