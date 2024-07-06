from fastapi import FastAPI
from kubernetes import client, config
from prometheus_client import start_http_server, Gauge

app = FastAPI()

@app.post("/createDeployment/{deployment_name}")
async def create_deployment(deployment_name: str):
    try:
        # Load local kube config for local testing
        config.load_kube_config()
        
        k8s_apps_v1 = client.AppsV1Api()
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={'app': deployment_name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={'app': deployment_name}),
                    spec=client.V1PodSpec(containers=[
                        client.V1Container(
                            name=deployment_name,
                            image="nginx",  # Replace with your desired image
                            ports=[client.V1ContainerPort(container_port=80)]
                        )
                    ])
                )
            )
        )
        k8s_apps_v1.create_namespaced_deployment(namespace="default", body=deployment)
        return {"message": f"Deployment {deployment_name} created successfully."}
    except Exception as e:
        return {"error": str(e)}

@app.get("/getPromdetails")
async def get_prom_details():
    try:
        # Load local kube config for local testing
        config.load_kube_config()
        
        k8s_api = client.CoreV1Api()
        pods = k8s_api.list_pod_for_all_namespaces().items
        pod_details = [{"name": pod.metadata.name, "namespace": pod.metadata.namespace} for pod in pods]
        return {"pod_details": pod_details}
    except Exception as e:
        return {"error": str(e)}

@app.get("/ping")
async def ping():
    return {"message": "Pong"}

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8001
    start_http_server(8001)
    import uvicorn
    # Run FastAPI application on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
