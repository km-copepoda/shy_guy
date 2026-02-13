output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id
}

output "s3_bucket_name" {
  description = "S3 bucket for frontend assets"
  value       = aws_s3_bucket.frontend.id
}

output "ecr_repository_url" {
  description = "ECR repository URL for backend Docker image"
  value       = aws_ecr_repository.backend.repository_url
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.backend.function_name
}

output "api_gateway_endpoint" {
  description = "API Gateway HTTP API endpoint"
  value       = aws_apigatewayv2_api.backend.api_endpoint
}
