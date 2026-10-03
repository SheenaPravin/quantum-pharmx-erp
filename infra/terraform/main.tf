terraform {
  required_version = ">= 1.6"
}
# AWS: ECS/EKS + RDS PostgreSQL + S3 + ElastiCache + OpenSearch + MSK + CloudWatch + IAM + KMS
# Fill per environment (dev → qa → uat → prod). Backend state in S3 + DynamoDB lock.
variable "env" { default = "dev" }
