kubectl delete -f secret.yaml
kubectl delete -f configmap.yaml
kubectl delete -f sectiondb-deploy-service.yaml
kubectl delete -f alert-deploy-service.yaml
kubectl delete -f camera-deploy-service.yaml
kubectl delete -f collector-deploy-service.yaml
kubectl delete -f face-recognition-deploy-service.yaml
kubectl delete -f image-analysis-deploy-service.yaml
kubectl delete -f mongoexpress-deploy-service.yaml
kubectl delete -f section-deploy-service.yaml
kubectl delete -f prometheus-deploy-service.yaml
kubectl delete -f grafana-deploy-service.yaml
kubectl delete -f path-based-ingressrules.yaml