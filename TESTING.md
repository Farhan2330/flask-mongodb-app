# Design Choices 

Environment Variables for Configuration:

- ConfigMap: ConfigMaps are used for non-sensitive data, while secrets are designed for sensitive information. ConfigMaps could be used for non-sensitive configuration data.

- Alternatives Considered:
- Kubernetes secrets:  Using environment variables to pass sensitive information like database credentials is secure and easily managed via Kubernetes secrets. This method also avoids hardcoding sensitive data directly into container images or configuration files.

#  Testing Scenarios

Autoscaling Test:

- Setup: Horizontal Pod Autoscaler (HPA) was configured for the Flask application using CPU utilization as a metric.

- Results:

  - Pods scaled up automatically when CPU utilization crossed the threshold (e.g., 70%).
  
  - Flask application responded well under load, maintaining response times.

  - After load decreased, pods scaled down, conserving resources.

Database Interaction Test:

- All operations were successful, confirming that the application correctly connected to MongoDB.

- Verified data persistence by restarting MongoDB pods and ensuring data was retained, confirming the functionality of the PVC.
  
- Issues Encountered:

  - Initial misconfiguration in MongoDB environment variables led to authentication failures. Correcting the secret keys resolved the issue.
