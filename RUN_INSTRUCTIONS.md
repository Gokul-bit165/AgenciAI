# Agenci AI: Run Instructions & Performance

## System Status
The system is **fully running**. 

## Performance Estimates
### Implementation
- **Startup Time**: The initial build took ~15 minutes (creating the "Brain" with OCR/ML support). **Future startups will be instant.**
- **Dashboard Load**: Instant.

### Validation Speed
- **CSV Processing**: 
  - For small files (e.g., `indian_providers.csv`, 50 rows): **~1-2 minutes**.
  - **Note**: Since the sample CSV lacks valid US NPIs, the agents will quickly flag them as "Not Found" and skip the slower enrichment steps.
- **PDF Processing**: ~5-10 seconds per page (OCR dependent).

## How to Access
1. **Dashboard**: Open [http://localhost:5173](http://localhost:5173) in your browser.
2. **Logs**: Check terminal for live agent activity.
