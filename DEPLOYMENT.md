# AutoFix v1.1 Deployment Guide

## Local Development Deployment

### Backend Deployment
```bash
cd AutoFix-backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with Azure credentials
uvicorn app.main:app --port 5000 --reload
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY AutoFix-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY AutoFix-backend/app ./app
ENV OPENAI_API_KEY=your-key
ENV AZURE_BASE_URL=your-base-url
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

## Configuration

### .autofixconfig.json
- project-level configuration
- Severity levels per error type
- Rule filtering options
- Debounce and max error settings

### Environment Variables
- OPENAI_API_KEY: Azure AI Foundry API key
- AZURE_BASE_URL: Cognitive Services endpoint
- LOG_LEVEL: Logging verbosity

## Scaling

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Run multiple backend instances
- Optional Redis for shared cache

### Database Storage
- Current: In-memory storage
- Production: Add PostgreSQL backend
- Implement persistent error history

## Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Key Metrics
- API latency (/analyze, /fix response times)
- Error rates and types
- Cache hit rate
- Rate limit violations

## Troubleshooting

### Backend unreachable
- Verify backend running: `curl http://localhost:5000/health`
- Check port 5000 not blocked
- Check firewall settings

### Rate limit exceeded
- Wait 60 seconds for window reset
- Increase debounce in config
- Deploy load balancer from multiple IPs

### Cache not working
- Clear VS Code cache
- Restart VS Code
- Check browser console for errors

## Version Upgrades

### v1.0 to v1.1
- Pull latest code
- Reinstall Python dependencies
- Reinstall npm packages
- Restart components
- No database migration needed

## Support

- GitHub Issues: https://github.com/Gkbdc01/AutoFix/issues
- Documentation: See FEATURES_v1.1.md
