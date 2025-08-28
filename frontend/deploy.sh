#!/bin/bash

# Deployment script for Angular Frontend
# Compatible with most cloud providers (Vercel, Netlify, AWS S3, etc.)

set -e  # Exit on any error

echo "🚀 Starting deployment process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi

    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18 or higher is required. Current version: $(node --version)"
        exit 1
    fi

    print_success "Node.js version: $(node --version)"
}

# Check if Angular CLI is installed
check_angular_cli() {
    if ! command -v ng &> /dev/null; then
        print_warning "Angular CLI not found. Installing globally..."
        npm install -g @angular/cli@latest
    fi
    print_success "Angular CLI version: $(ng version --json | grep -o '"version":"[^"]*' | cut -d'"' -f4)"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."

    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi

    print_success "Dependencies installed successfully"
}

# Run tests (optional)
run_tests() {
    if [ "$SKIP_TESTS" != "true" ]; then
        print_status "Running tests..."
        npm run test -- --watch=false --browsers=ChromeHeadless || {
            print_warning "Tests failed, but continuing with deployment..."
        }
    else
        print_warning "Skipping tests (SKIP_TESTS=true)"
    fi
}

# Build for production
build_production() {
    print_status "Building application for production..."

    # Set production API URL if provided
    if [ ! -z "$PROD_API_URL" ]; then
        print_status "Using production API URL: $PROD_API_URL"
        # Update environment.prod.ts with the provided API URL
        sed -i.bak "s|https://your-production-backend-url.com|$PROD_API_URL|g" src/environments/environment.prod.ts
    fi

    npm run build

    print_success "Production build completed successfully"

    # Display build statistics
    if [ -d "dist" ]; then
        BUILD_SIZE=$(du -sh dist/ | cut -f1)
        print_success "Build size: $BUILD_SIZE"

        # List main files
        print_status "Main build files:"
        find dist/ -name "*.js" -o -name "*.css" | head -10 | while read file; do
            FILE_SIZE=$(du -h "$file" | cut -f1)
            echo "  - $(basename "$file"): $FILE_SIZE"
        done
    fi
}

# Deployment functions for different platforms

deploy_vercel() {
    print_status "Deploying to Vercel..."

    if ! command -v vercel &> /dev/null; then
        print_status "Installing Vercel CLI..."
        npm install -g vercel
    fi

    vercel --prod
    print_success "Deployed to Vercel successfully!"
}

deploy_netlify() {
    print_status "Deploying to Netlify..."

    if ! command -v netlify &> /dev/null; then
        print_status "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi

    netlify deploy --prod --dir=dist/frontend
    print_success "Deployed to Netlify successfully!"
}

deploy_aws_s3() {
    if [ -z "$AWS_S3_BUCKET" ]; then
        print_error "AWS_S3_BUCKET environment variable is required for S3 deployment"
        exit 1
    fi

    print_status "Deploying to AWS S3 bucket: $AWS_S3_BUCKET"

    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install and configure AWS CLI."
        exit 1
    fi

    # Sync files to S3
    aws s3 sync dist/frontend s3://$AWS_S3_BUCKET --delete

    # Invalidate CloudFront if distribution ID is provided
    if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        print_status "Invalidating CloudFront distribution: $CLOUDFRONT_DISTRIBUTION_ID"
        aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
    fi

    print_success "Deployed to AWS S3 successfully!"
}

deploy_github_pages() {
    print_status "Deploying to GitHub Pages..."

    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI is not installed. Please install gh CLI or deploy manually."
        exit 1
    fi

    # Build with base href for GitHub Pages
    ng build --base-href "/$GITHUB_REPO_NAME/"

    # Deploy to gh-pages branch
    npx angular-cli-ghpages --dir=dist/frontend

    print_success "Deployed to GitHub Pages successfully!"
}

# Create deployment info file
create_deployment_info() {
    print_status "Creating deployment info..."

    DEPLOYMENT_INFO="dist/deployment-info.json"

    cat > $DEPLOYMENT_INFO << EOF
{
  "deploymentDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "$(npm pkg get version | tr -d '"')",
  "commit": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
  "branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')",
  "buildEnvironment": "production",
  "nodeVersion": "$(node --version)",
  "angularVersion": "$(ng version --json 2>/dev/null | grep -o '"version":"[^"]*' | head -1 | cut -d'"' -f4 || echo 'unknown')"
}
EOF

    print_success "Deployment info created: $DEPLOYMENT_INFO"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."

    # Restore original environment file if it was modified
    if [ -f "src/environments/environment.prod.ts.bak" ]; then
        mv src/environments/environment.prod.ts.bak src/environments/environment.prod.ts
    fi

    print_success "Cleanup completed"
}

# Main deployment function
main() {
    print_status "=== Frontend Deployment Script ==="
    print_status "Starting deployment process..."

    # Change to script directory
    cd "$(dirname "$0")"

    # Check prerequisites
    check_node
    check_angular_cli

    # Install dependencies
    install_dependencies

    # Run tests (optional)
    run_tests

    # Build for production
    build_production

    # Create deployment info
    create_deployment_info

    # Deploy based on platform
    case "${DEPLOY_PLATFORM:-manual}" in
        "vercel")
            deploy_vercel
            ;;
        "netlify")
            deploy_netlify
            ;;
        "aws-s3")
            deploy_aws_s3
            ;;
        "github-pages")
            deploy_github_pages
            ;;
        "manual")
            print_success "Build completed! Manual deployment required."
            print_status "Build files are in: dist/frontend"
            print_status "Upload these files to your web server."
            ;;
        *)
            print_warning "Unknown deployment platform: $DEPLOY_PLATFORM"
            print_status "Available platforms: vercel, netlify, aws-s3, github-pages, manual"
            ;;
    esac

    print_success "=== Deployment process completed! ==="
}

# Handle script interruption
trap cleanup EXIT

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            DEPLOY_PLATFORM="$2"
            shift 2
            ;;
        --api-url)
            PROD_API_URL="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --platform PLATFORM    Deployment platform (vercel, netlify, aws-s3, github-pages, manual)"
            echo "  --api-url URL          Production API URL"
            echo "  --skip-tests           Skip running tests"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  DEPLOY_PLATFORM        Deployment platform"
            echo "  PROD_API_URL          Production API URL"
            echo "  AWS_S3_BUCKET         AWS S3 bucket name (for aws-s3 platform)"
            echo "  CLOUDFRONT_DISTRIBUTION_ID  CloudFront distribution ID (optional)"
            echo "  GITHUB_REPO_NAME      GitHub repository name (for github-pages platform)"
            echo "  SKIP_TESTS            Skip tests (true/false)"
            echo ""
            echo "Examples:"
            echo "  $0 --platform vercel --api-url https://api.example.com"
            echo "  $0 --platform aws-s3 --api-url https://api.example.com"
            echo "  DEPLOY_PLATFORM=netlify PROD_API_URL=https://api.example.com $0"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
