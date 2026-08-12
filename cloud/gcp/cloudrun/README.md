To generate sample data via Google Cloud Run service

Step 1 : Autheticate via gcloud CLI and pick the right project

Step 2 : Use these gcloud commands to create and manage a sample app

```
gcloud run deploy hello-cloud-run \
  --image=us-docker.pkg.dev/cloudrun/container/hello \
  --platform=managed \
  --region=asia-south1 \
  --allow-unauthenticated
```

```
gcloud run services describe hello-cloud-run \
  --region=asia-south1 \
  --format='value(status.url)'
```

```
curl "$(gcloud run services describe hello-cloud-run \
  --region=asia-south1 \
  --format='value(status.url)')"
```

```
gcloud run services delete hello-cloud-run \
  --region=asia-south1
```