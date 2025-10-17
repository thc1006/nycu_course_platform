# Deployment Guide - NYCU Course Platform

Comprehensive guide for deploying the NYCU Course Platform in various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Production Checklist](#production-checklist)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required Software

- **Docker**: >= 24.0
- **Docker Compose**: >= 2.20
- **Kubernetes**: >= 1.28 (for K8s deployment)
- **kubectl**: Latest version
- **Node.js**: >= 22 (for local frontend dev)
- **Python**: >= 3.13 (for local backend dev)
- **PostgreSQL**: >= 16

### Optional Tools

- **k9s**: Kubernetes cluster management
- **helm**: Package manager for Kubernetes
- **kubectl-neat**: Clean kubectl output

## Local Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with API URL
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend unit tests
cd frontend
npm test

# Frontend E2E tests
npm run e2e
```

## Docker Deployment

### Using Docker Compose (Recommended for Development)

1. **Environment Configuration**

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_DB=nycu_courses
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=your_redis_password_here
REDIS_PORT=6379

# Backend
BACKEND_PORT=8000
LOG_LEVEL=info

# Frontend
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# Nginx
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```

2. **Build and Start Services**

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

3. **Individual Service Management**

```bash
# Start specific service
docker-compose up -d backend

# Restart service
docker-compose restart frontend

# View service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -m pytest
```

4. **Run Scraper**

```bash
# One-time scraper run
docker-compose run --rm scraper

# With specific profile
docker-compose --profile scraper up
```

### Building Individual Images

```bash
# Backend
docker build -t nycu-platform/backend:latest ./backend

# Frontend
docker build -t nycu-platform/frontend:latest ./frontend

# Scraper
docker build -t nycu-platform/scraper:latest ./scraper
```

## Kubernetes Deployment

### Prerequisites

1. **Kubernetes Cluster** (any of the following):
   - Minikube (local testing)
   - Kind (local testing)
   - GKE (Google Kubernetes Engine)
   - EKS (Amazon Elastic Kubernetes Service)
   - AKS (Azure Kubernetes Service)
   - Self-managed cluster

2. **Container Registry**:
   - Docker Hub
   - Google Container Registry
   - Amazon ECR
   - Azure Container Registry
   - Harbor (self-hosted)

### Deployment Steps

1. **Configure kubectl**

```bash
# Verify cluster connection
kubectl cluster-info
kubectl get nodes
```

2. **Update Image References**

Edit `k8s/kustomization.yaml` to point to your container registry:

```yaml
images:
  - name: nycu-platform/backend
    newName: your-registry/nycu-platform-backend
    newTag: v1.0.0
  - name: nycu-platform/frontend
    newName: your-registry/nycu-platform-frontend
    newTag: v1.0.0
```

3. **Update Secrets**

**IMPORTANT**: Never commit real secrets to Git!

```bash
# Create secrets from command line
kubectl create secret generic nycu-platform-secrets \
  --from-literal=POSTGRES_PASSWORD='your-secure-password' \
  --from-literal=DATABASE_URL='postgresql://user:pass@postgres-service:5432/nycu_courses' \
  --namespace=nycu-platform

# Or use Sealed Secrets (recommended)
kubeseal --format=yaml < k8s/secrets.yaml > k8s/sealed-secrets.yaml
kubectl apply -f k8s/sealed-secrets.yaml
```

4. **Deploy with kubectl**

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply all configurations
kubectl apply -f k8s/

# Or use Kustomize
kubectl apply -k k8s/

# Verify deployment
kubectl get all -n nycu-platform
```

5. **Check Deployment Status**

```bash
# Check pods
kubectl get pods -n nycu-platform

# Check services
kubectl get services -n nycu-platform

# Check logs
kubectl logs -f deployment/backend -n nycu-platform

# Describe pod for troubleshooting
kubectl describe pod <pod-name> -n nycu-platform
```

6. **Access the Application**

```bash
# Port forwarding (for testing)
kubectl port-forward service/frontend-service 3000:3000 -n nycu-platform
kubectl port-forward service/backend-service 8000:8000 -n nycu-platform

# Or configure Ingress (see below)
```

### Ingress Configuration

1. **Install Ingress Controller**

```bash
# Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml

# Verify installation
kubectl get pods -n ingress-nginx
```

2. **Update DNS**

Point your domain to the Ingress LoadBalancer IP:

```bash
# Get LoadBalancer IP
kubectl get svc -n ingress-nginx

# Update DNS records:
# nycu-platform.example.com -> LoadBalancer IP
# api.nycu-platform.example.com -> LoadBalancer IP
```

3. **Configure TLS (Optional but Recommended)**

Install cert-manager for automatic TLS:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n nycu-platform

# Check HPA status
kubectl get hpa -n nycu-platform

# Describe HPA
kubectl describe hpa backend-hpa -n nycu-platform
```

### Updates and Rollouts

```bash
# Update image
kubectl set image deployment/backend backend=your-registry/backend:v1.1.0 -n nycu-platform

# Check rollout status
kubectl rollout status deployment/backend -n nycu-platform

# Rollback if needed
kubectl rollout undo deployment/backend -n nycu-platform

# View rollout history
kubectl rollout history deployment/backend -n nycu-platform
```

## Production Checklist

### Security

- [ ] Change all default passwords
- [ ] Use secrets management (Sealed Secrets, Vault)
- [ ] Enable HTTPS/TLS
- [ ] Configure network policies
- [ ] Enable RBAC
- [ ] Run containers as non-root user
- [ ] Scan images for vulnerabilities
- [ ] Set up firewall rules
- [ ] Enable audit logging

### Performance

- [ ] Configure resource limits and requests
- [ ] Enable horizontal pod autoscaling
- [ ] Set up CDN for static assets
- [ ] Configure database connection pooling
- [ ] Enable Redis caching
- [ ] Optimize Docker images (multi-stage builds)
- [ ] Configure compression (gzip/brotli)

### Reliability

- [ ] Set up health checks (liveness/readiness probes)
- [ ] Configure pod disruption budgets
- [ ] Enable rolling updates
- [ ] Set up database backups
- [ ] Configure persistent volumes
- [ ] Implement retry logic
- [ ] Set up graceful shutdown

### Monitoring

- [ ] Set up logging (ELK, Loki, CloudWatch)
- [ ] Configure metrics (Prometheus, Grafana)
- [ ] Set up alerting (PagerDuty, Slack)
- [ ] Enable tracing (Jaeger, Zipkin)
- [ ] Monitor resource usage
- [ ] Track error rates
- [ ] Set up uptime monitoring

### Backup and Disaster Recovery

- [ ] Database backup strategy
- [ ] Test backup restoration
- [ ] Document recovery procedures
- [ ] Set up multi-region deployment (if needed)
- [ ] Configure cross-region replication

## Monitoring and Maintenance

### Logs

```bash
# View all logs
kubectl logs -f -l app=backend -n nycu-platform

# View logs from specific pod
kubectl logs <pod-name> -n nycu-platform

# Previous container logs
kubectl logs <pod-name> --previous -n nycu-platform
```

### Metrics

```bash
# Resource usage
kubectl top nodes
kubectl top pods -n nycu-platform

# Detailed pod info
kubectl describe pod <pod-name> -n nycu-platform
```

### Database Maintenance

```bash
# Connect to database
kubectl exec -it postgres-0 -n nycu-platform -- psql -U postgres

# Backup database
kubectl exec -it postgres-0 -n nycu-platform -- pg_dump -U postgres nycu_courses > backup.sql

# Restore database
cat backup.sql | kubectl exec -i postgres-0 -n nycu-platform -- psql -U postgres nycu_courses
```

### Cleanup

```bash
# Delete specific resource
kubectl delete deployment backend -n nycu-platform

# Delete all resources in namespace
kubectl delete all --all -n nycu-platform

# Delete namespace
kubectl delete namespace nycu-platform
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n nycu-platform
   kubectl logs <pod-name> -n nycu-platform
   ```

2. **Image pull errors**
   - Verify image exists in registry
   - Check imagePullSecrets
   - Verify network connectivity

3. **Database connection issues**
   - Check DATABASE_URL secret
   - Verify postgres service is running
   - Check network policies

4. **Ingress not working**
   - Verify ingress controller is running
   - Check DNS configuration
   - Review ingress logs

### Support

For issues or questions:
- Check logs first
- Review Kubernetes events
- Consult documentation
- Open an issue on GitHub

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
