#!/bin/bash
# deploy.sh
# ---------
# One-click deployment script for TeachClear on Google Cloud Run.
# Reads credentials from .env file — no hardcoded secrets.
#
# Usage (Mac/Linux):
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Usage (Windows PowerShell):
#   bash deploy.sh
#   (requires Git Bash or WSL)

# ── Load variables from .env ───────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "❌ .env file not found. Please create it in the project root."
  exit 1
fi

# Export each non-comment, non-empty line from .env
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# ── Validate required variables ────────────────────────────────────────────────
if [ -z "$TELEGRAM_TOKEN" ]; then
  echo "❌ TELEGRAM_TOKEN is missing from .env"
  exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
  echo "❌ GEMINI_API_KEY is missing from .env"
  exit 1
fi

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_ID=$(gcloud config get-value project)   # reads current active project
SERVICE_NAME="teach-clear"
REGION="asia-south1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-3.1-flash-lite-preview}" # use .env value or default

echo "📋 Deploying with:"
echo "   Project  : $PROJECT_ID"
echo "   Service  : $SERVICE_NAME"
echo "   Region   : $REGION"
echo "   Model    : $GEMINI_MODEL"
echo ""

# ── Step 1: Build and push Docker image ───────────────────────────────────────
echo "🔨 Building Docker image..."
gcloud builds submit --tag $IMAGE

if [ $? -ne 0 ]; then
  echo "❌ Docker build failed. Check the errors above."
  exit 1
fi

# ── Step 2: Deploy to Cloud Run ───────────────────────────────────────────────
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --timeout 120 \
  --set-env-vars "TELEGRAM_TOKEN=$TELEGRAM_TOKEN,GEMINI_API_KEY=$GEMINI_API_KEY,GEMINI_MODEL=$GEMINI_MODEL"

if [ $? -ne 0 ]; then
  echo "❌ Deployment failed. Check the errors above."
  exit 1
fi

# ── Step 3: Get the deployed URL ──────────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format "value(status.url)")

echo ""
echo "✅ Deployed successfully!"
echo "📍 Service URL: $SERVICE_URL"
echo ""

# ── Step 4: Set WEBHOOK_URL in Cloud Run ──────────────────────────────────────
echo "🔗 Setting WEBHOOK_URL..."
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars WEBHOOK_URL=$SERVICE_URL

echo ""
echo "⚠️  One final step — register webhook with Telegram:"
echo "   Open this URL in your browser:"
echo "   $SERVICE_URL/set_webhook"
echo ""
echo "   You should see: ✅ Webhook set to: $SERVICE_URL/webhook"
