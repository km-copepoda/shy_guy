#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== 1. Terraform Apply ==="
cd "$SCRIPT_DIR"
terraform init -input=false
terraform apply -auto-approve

# Read outputs
ECR_REPO=$(terraform output -raw ecr_repository_url)
LAMBDA_NAME=$(terraform output -raw lambda_function_name)
S3_BUCKET=$(terraform output -raw s3_bucket_name)
CF_DIST_ID=$(terraform output -raw cloudfront_distribution_id)
AWS_REGION=$(terraform output -raw 2>/dev/null || echo "ap-northeast-1")

# Extract ECR registry for docker login
ECR_REGISTRY="${ECR_REPO%%/*}"

echo "=== 2. Docker Build & Push ==="
cd "$PROJECT_ROOT/backend"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"
docker build --platform linux/amd64 -t "$ECR_REPO:latest" .
docker push "$ECR_REPO:latest"

echo "=== 3. Update Lambda ==="
aws lambda update-function-code \
  --function-name "$LAMBDA_NAME" \
  --image-uri "$ECR_REPO:latest" \
  --region "$AWS_REGION" \
  --no-cli-pager

echo "Waiting for Lambda update to complete..."
aws lambda wait function-updated \
  --function-name "$LAMBDA_NAME" \
  --region "$AWS_REGION"

echo "=== 4. Frontend Build & Deploy ==="
cd "$PROJECT_ROOT/frontend"
npm ci
npm run build
aws s3 sync dist/ "s3://$S3_BUCKET" --delete

echo "=== 5. CloudFront Cache Invalidation ==="
aws cloudfront create-invalidation \
  --distribution-id "$CF_DIST_ID" \
  --paths "/*" \
  --no-cli-pager

echo ""
echo "=== Deploy Complete ==="
CLOUDFRONT_DOMAIN=$(cd "$SCRIPT_DIR" && terraform output -raw cloudfront_domain)
echo "URL: https://$CLOUDFRONT_DOMAIN"
