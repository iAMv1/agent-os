---
name: devops-engineer
description: Use when you need to design CI/CD pipelines, containerize applications, configure Kubernetes, or write infrastructure as code. Covers Docker, Kubernetes, GitHub Actions, Terraform, and cloud infrastructure best practices.
when_to_use: Setting up deployment pipelines, containerizing applications, designing cloud infrastructure, configuring Kubernetes deployments, writing Terraform/Pulumi code, or optimizing build and deployment processes.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - platform
  - scope
  - complexity
argument-hint: "[github-actions|gitlab-ci|docker|kubernetes|terraform|aws|gcp|azure] [pipeline|container|infra|full-stack] [simple|standard|enterprise]"
---

# DevOps Engineer

Design and implement production-grade CI/CD pipelines, containerized deployments, Kubernetes configurations, and infrastructure as code. Focuses on reliability, security, and automation.

<HARD-GATE>
Do NOT write infrastructure code without considering rollback procedures. Do NOT create Docker images without security scanning. Do NOT design CI/CD pipelines without testing stages. Do NOT deploy to production without environment parity and monitoring.
</HARD-GATE>

## The Iron Law

Every deployment artifact must be: reproducible from source, versioned, tested, scanned for vulnerabilities, and accompanied by a rollback procedure.

## When to Use

- Setting up CI/CD pipelines for a project
- Containerizing an application with Docker
- Designing Kubernetes deployments
- Writing infrastructure as code (Terraform, Pulumi)
- Configuring cloud resources (AWS, GCP, Azure)
- Optimizing build times or deployment processes
- Setting up monitoring and alerting
- Designing disaster recovery procedures

## When NOT to Use

- Single-server applications with no scaling needs
- When a PaaS (Vercel, Heroku, Railway) solves the problem
- Prototyping where infrastructure will change daily
- When you lack credentials or access to the target environment

## The Process

### Phase 1: CI/CD Pipeline Design

1. **Define pipeline stages**
   ```
   Pipeline Stages:
   ├── Trigger: What starts the pipeline?
   │   ├── Push to branch
   │   ├── Pull request
   │   ├── Tag creation
   │   └── Scheduled (cron)
   ├── Build: Compile, bundle, containerize
   ├── Test: Unit, integration, security, lint
   ├── Quality: Code coverage, complexity, duplication
   ├── Security: Dependency scan, SAST, container scan
   ├── Deploy: To staging, then production
   └── Verify: Smoke tests, health checks, monitoring
   ```

2. **GitHub Actions pipeline**
   ```yaml
   name: CI/CD Pipeline
   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-node@v4
           with:
             node-version: '20'
             cache: 'npm'
         - run: npm ci
         - run: npm run lint
         - run: npm test -- --coverage
         - uses: actions/upload-artifact@v4
           if: always()
           with:
             name: test-results
             path: coverage/

     security:
       needs: test
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - run: npm audit --audit-level=high
         - uses: aquasecurity/trivy-action@master
           with:
             scan-type: 'fs'
             severity: 'CRITICAL,HIGH'

     build:
       needs: [test, security]
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - run: docker build -t app:${{ github.sha }} .
         - run: docker push registry/app:${{ github.sha }}

     deploy-staging:
       needs: build
       if: github.ref == 'refs/heads/main'
       runs-on: ubuntu-latest
       environment: staging
       steps:
         - run: kubectl set image deployment/app app=registry/app:${{ github.sha }}
         - run: kubectl rollout status deployment/app --timeout=300s

     deploy-production:
       needs: deploy-staging
       if: github.ref == 'refs/heads/main'
       runs-on: ubuntu-latest
       environment: production
       steps:
         - run: kubectl set image deployment/app app=registry/app:${{ github.sha }}
         - run: kubectl rollout status deployment/app --timeout=300s
   ```

3. **Pipeline best practices**
   - Pin action versions (no `@main` or `@latest`)
   - Use OIDC for cloud provider authentication (no long-lived secrets)
   - Cache dependencies between runs
   - Fail fast — run lint and typecheck before expensive tests
   - Use environments for deployment approval gates
   - Store artifacts for debugging failed runs
   - Set timeout limits on all jobs

### Phase 2: Docker & Containerization

4. **Dockerfile best practices**
   ```dockerfile
   # Multi-stage build for minimal image
   FROM node:20-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production
   COPY . .
   RUN npm run build

   FROM node:20-alpine AS runner
   WORKDIR /app

   # Non-root user
   RUN addgroup -g 1001 -S appgroup && \
       adduser -S appuser -u 1001 -G appgroup

   # Production dependencies only
   COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
   COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
   COPY --from=builder --chown=appuser:appgroup /app/package.json ./

   USER appuser

   # Health check
   HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
     CMD wget -qO- http://localhost:3000/health || exit 1

   EXPOSE 3000
   CMD ["node", "dist/index.js"]
   ```

5. **Container security**
   - Use minimal base images (alpine, distroless, scratch)
   - Run as non-root user
   - Multi-stage builds to exclude build tools
   - No secrets in image layers (use build secrets or runtime env)
   - Scan images for vulnerabilities (Trivy, Grype)
   - Sign images (Cosign, Notary)
   - Pin base image digests, not tags

6. **Docker Compose for development**
   ```yaml
   services:
     app:
       build: .
       ports: ["3000:3000"]
       environment:
         - DATABASE_URL=postgres://postgres:postgres@db:5432/app
       depends_on:
         db:
           condition: service_healthy
       volumes:
         - .:/app
         - /app/node_modules

     db:
       image: postgres:16-alpine
       environment:
         POSTGRES_DB: app
         POSTGRES_PASSWORD: postgres
       ports: ["5432:5432"]
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U postgres"]
         interval: 5s
         timeout: 3s
         retries: 5
       volumes:
         - pgdata:/var/lib/postgresql/data

   volumes:
     pgdata:
   ```

### Phase 3: Kubernetes

7. **Deployment configuration**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: app
     labels:
       app: app
       version: "1.0.0"
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: app
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 0
     template:
       metadata:
         labels:
           app: app
           version: "1.0.0"
       spec:
         securityContext:
           runAsNonRoot: true
           runAsUser: 1001
         containers:
         - name: app
           image: registry/app:1.0.0
           ports:
           - containerPort: 3000
           resources:
             requests:
               memory: "128Mi"
               cpu: "100m"
             limits:
               memory: "256Mi"
               cpu: "500m"
           readinessProbe:
             httpGet:
               path: /health
               port: 3000
             initialDelaySeconds: 5
             periodSeconds: 10
           livenessProbe:
             httpGet:
               path: /health
               port: 3000
             initialDelaySeconds: 15
             periodSeconds: 20
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: app-secrets
                 key: database-url
   ```

8. **Service and Ingress**
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: app
   spec:
     selector:
       app: app
     ports:
     - port: 80
       targetPort: 3000
     type: ClusterIP
   ---
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: app
     annotations:
       cert-manager.io/cluster-issuer: letsencrypt
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
   spec:
     tls:
     - hosts:
       - app.example.com
       secretName: app-tls
     rules:
     - host: app.example.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: app
               port:
                 number: 80
   ```

9. **Kubernetes best practices**
   - Always set resource requests and limits
   - Use readiness and liveness probes
   - Deploy with PodDisruptionBudgets
   - Use NetworkPolicies to restrict traffic
   - Store secrets in Kubernetes Secrets (or external secret manager)
   - Use ConfigMaps for configuration
   - Set up Horizontal Pod Autoscaler for variable load
   - Use namespaces to isolate environments

### Phase 4: Infrastructure as Code

10. **Terraform structure**
    ```
    terraform/
    ├── main.tf          # Provider and resource definitions
    ├── variables.tf     # Input variables with descriptions
    ├── outputs.tf       # Output values
    ├── locals.tf        # Local values
    ├── versions.tf      # Provider version constraints
    ├── environments/
    │   ├── dev.tfvars
    │   ├── staging.tfvars
    │   └── prod.tfvars
    └── modules/
        ├── vpc/
        ├── ecs/
        └── rds/
    ```

11. **Terraform best practices**
    - Pin provider versions
    - Use modules for reusability
    - Store state remotely (S3 + DynamoDB for locking)
    - Use workspaces or separate state files per environment
    - Run `terraform plan` before `apply` in CI
    - Use `terraform validate` and `tflint` in CI
    - Never store secrets in Terraform state (use external secret managers)

12. **Infrastructure checklist**
    - [ ] VPC with public and private subnets
    - [ ] NAT gateway for private subnet outbound
    - [ ] Security groups with least-privilege rules
    - [ ] IAM roles with minimum required permissions
    - [ ] Encryption at rest (RDS, EBS, S3)
    - [ ] Encryption in transit (TLS)
    - [ ] Backup and disaster recovery plan
    - [ ] Monitoring and alerting configured
    - [ ] Cost optimization (right-sizing, spot instances)

## Anti-Slop Rules

<Good>
- "Dockerfile uses multi-stage build with node:20-alpine, runs as non-root user (UID 1001), includes HEALTHCHECK, and pins npm dependencies with npm ci."
- "CI pipeline runs lint → test → security scan → build → deploy-staging → deploy-production with manual approval gate for production."
- "Kubernetes deployment sets resource requests (128Mi/100m) and limits (256Mi/500m), includes readiness/liveness probes, and uses RollingUpdate with maxUnavailable=0 for zero-downtime deploys."
</Good>

<Bad>
- "FROM node:latest" — unpinned, mutable tag
- "RUN npm install" — not reproducible, use npm ci
- Running containers as root
- No health checks defined
- Secrets hardcoded in Dockerfile or environment files
- No resource limits on Kubernetes pods
- Terraform state stored locally
- No rollback strategy for deployments
</Bad>

## CI/CD Pipeline Patterns

| Pattern | Use Case | Complexity |
|---------|----------|-----------|
| **Simple** | Single app, single environment | Build → Test → Deploy |
| **Standard** | Multi-environment, PR checks | PR: lint+test → Main: build+deploy staging → Manual: deploy prod |
| **Enterprise** | Multi-service, compliance | PR: all checks → Staging: auto → Prod: approval + canary + rollback |

## Monitoring & Observability Checklist

- [ ] Application metrics (request rate, error rate, latency)
- [ ] Infrastructure metrics (CPU, memory, disk, network)
- [ ] Log aggregation (structured JSON logs)
- [ ] Distributed tracing for microservices
- [ ] Alerting on SLO breaches
- [ ] Dashboard for key metrics
- [ ] Runbook for common incidents
- [ ] PagerDuty/Opsgenie integration for critical alerts

## Integration

Related skills: `security-auditor`, `code-reviewer`, `api-designer`, `database-designer`
