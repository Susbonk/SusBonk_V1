# Frontend Deployment Guide

## Development

```bash
npm install
npm run dev
```

Runs Vite dev server on `http://localhost:5173`

## Production Build

### Local Build
```bash
npm run build
npm run preview
```

### Docker Build
```bash
docker build -t susbonk-frontend .
docker run -p 3000:3000 susbonk-frontend
```

## Runtime Configuration

### Package Manager
- **Standard**: npm with `package-lock.json`
- Lockfile is committed for reproducible builds
- Use `npm ci` in CI/CD for exact dependency versions

### Serving Strategy
- **Development**: Vite dev server (port 5173)
- **Production**: nginx serving static files (port 3000)
- **API Proxy**: nginx forwards `/api/*` to backend service

## Docker Configuration

### Multi-stage Build
1. **Builder stage**: Node 20 Alpine, runs `npm ci` and `npm run build`
2. **Runner stage**: nginx Alpine, serves static files from `/usr/share/nginx/html`

### nginx Configuration
- SPA routing: All routes fallback to `index.html`
- API proxy: `/api/*` → `http://api-backend:8000/`
- Static asset caching: 1 year for immutable assets
- Gzip compression enabled

### Files
- `Dockerfile`: Multi-stage build configuration
- `nginx.conf`: Production server configuration
- `.dockerignore`: Excludes unnecessary files from build context
- `package-lock.json`: Locked dependency versions

## Environment Variables

Create `.env` file (see `.env.example`):
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Build Verification

```bash
# Check build output
npm run build
ls -lh dist/

# Test production build locally
npm run preview

# Test Docker build
docker build -t test-frontend .
docker run -p 3000:3000 test-frontend
curl http://localhost:3000
```

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Install dependencies
  run: npm ci
  
- name: Build
  run: npm run build
  
- name: Build Docker image
  run: docker build -t frontend:${{ github.sha }} .
```

## Troubleshooting

### Build fails with dependency errors
```bash
rm -rf node_modules package-lock.json
npm install
```

### Docker build is slow
- Ensure `.dockerignore` excludes `node_modules` and `dist`
- Use Docker layer caching in CI/CD

### API requests fail in production
- Check nginx proxy configuration in `nginx.conf`
- Verify backend service name matches docker-compose network
- Check CORS settings on backend
