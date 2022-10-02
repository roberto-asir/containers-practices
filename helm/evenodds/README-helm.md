# PRACTICA Final - Contenedores: más que VMs 

## Helm

Sección relacionada con Helm y sus charts de la práctica final del módulo `Contenedores: más que VMs`

## Índice:
- [Objetivos](#objetivos)
- [Pasos para desplegar el chart](#pasos-para-desplegar-el-chart)
- [Values.yaml](#valuesyaml)
- [Comprobar el despliegue](#comprobar-el-despliegue)


## Objetivos

En esta sección se cubren los siguientes puntos de la práctica relacionados con manifiestos de Kubernetes: 8-17 y 19.

En todos los archivos del chart creado se usan valores del fichero values.yaml

En siete de ellos  se utilizan estructuras de control if, with o range

El fichero values.yaml está auto documentado en cada uno de los valores que hay configurable apareciendo posibles configuraciones comentadas a falta de descomentarlas a modo de ayuda.

Hay 

## Pasos para desplegar el chart

Para desplegar el chart ejecuta desde el directorio raiz:
`helm install kkkk helm/evenodds/`


## Values.yaml

Las partes más significativas de la configuración del chart son:

La aplicación es configurable en los siguientes campos en values.yaml:
- app_deployment.yaml:
Recursos del pod:
  - requestsMemory: "64Mi"
  - requestsCpu: "150m"
  - limitsMemory: "128Mi"
  - limitsCpu: "400m"

La versión de la imagen:
  - imageVersion: "v0.5"

Pod antiaffinity en la aplicación.


- ddbb_deployment.yaml
  - Pod affinity en el pod de la base e datos
  - Los datos de conexión a la base de configurables en values.yaml en texto plano (se convierte a base64 en la plantilla del fichero) se configuran realmente para el secret `ddbb-secret-evenodds.yaml pero se importan como variables de entorno desde esta plantilla.

- service-evenodds.yaml
  En caso de que se use ingress el servicio de acceso a la aplicación se configura como ClusterIP y en caso contrario como LoadBalancer para permitir acceso del exterior.



Hay secciones opcionales que tienen un código por defecto comentado y con instrucciones de configuración relacionadas con certificados y el ingress.




```yaml
##### ns_evenodds.yaml
## Namespaces used for the chart
## uncomment to use default value
## to run two instances it must be changed:
namespace: evenodds-helm-ns
##### end - ns_evenodds.yaml


###### cf_app.yaml values
# max logs file size to set into application to rotation logs 
cfApp:
  maxLogsSize: "20m"
# number of aplication logs to rotate set into application to rotation logs 
  maxLogsFiles: "10"
###### end - cf_app.yaml values


###### app_deployment.yaml values

# Deployment anotations to set elastic json logging
appDeployment:
  appPodAnnotations:
    annotations:
      co.elastic.logs.json-logging/json.keys_under_root: "true"
      co.elastic.logs.json-logging/json.add_error_key: "true"
      co.elastic.logs.json-logging/json.message_key: "message"

# Set app pods affinity 
# One instance per node no mandatory
  affinity: true
 

# container resources
  requestsMemory: "64Mi"
  requestsCpu: "150m"
  limitsMemory: "128Mi"
  limitsCpu: "400m"
# end - container resources

# container image version
  imageVersion: "v0.5"

###### end - app_deployment.yaml values


###### ddbb-secret-evenodds file
# Values for data secret
dbSecret:
  psDb: enchante
  psUser: enchante
  psPass: enchante
###### end - ddbb-secret-evenodds file

###### ddbb_deployment.yaml values
ddbbDeployment:
  # statefullSet workload, keep in mind
  replicas: 1

  # labels to elastick autodetect postgres
  elasticLogs:
    co.elastic.metrics/enabled: "true"
    co.elastic.metrics/module: "postgres"
    co.elastic.metrics/hosts: '${data.host}:5432'
    co.elastic.metrics/period: 1m
    co.elastic.logs/enabled: "true"
    co.elastic.logs/module: "postgres"

  ### OPTIONAL - affinity with app pods
  # comment this block to avoid implement the afinity
  podAffinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - podAffinityTerm:
            labelSelector:
              matchLabels:
                app: evenodds-app
            namespaces:
              - "evenodds-ns"
            topologyKey: kubernetes.io/hostname
          weight: 1
  ### OPTIONALend - affinity with app pods

  # usefull to debug
  terminationGracePeriodSeconds: "90"

  # postgres image version:
  imageVersion: "15beta4-alpine3.16"

  # PV size in gigas: set de gigas number desired only
  pvGBSize: 1
###### end - ddbb_deployment.yaml values

##### autoscale-evenodds.yaml

### OPTIONAL - uncomment and set proper values:
autoscale: 
  maxReplicas: 5
  minReplicas: 2
  targetCPUUtilizationPercentage: 70

##### OPTIONALend - autoscale-evenodds.yaml

##### OPTIONAL - cluster-issuer-letsencrypt-evenodds.yaml
### IMPORTANT !!!
### Is necesary a Let's encrypt cert manager
### installed previously in the cluster
### https://cert-manager.io/docs/installation/helm/

# letsEncrypt:
#   # define the kind of cert asked on env variable
#   # two options:
#   # - "prod" for valid certificate
#   # - anything else ("stagin" by default) for a staging certificate
#   env: "staging"

##### OPTIONALend - cluster-issuer-letsencrypt-evenodds.yaml



##### OPTIONAL - ingress-evenodds.yaml
### IMPORTANT !!!
### Is necesary an nginx ingress controller
### installed previously in the cluster
### https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/
### this chart can install it with default configuration
### setting installNginxIngressController variable to true

# To activate uncomment next block lines and configure values:
# ingress:
#   ## public access port
#   port: 80
#   ## dns name of access host
#   ## It's used as host in a certificate order
#   ## so the domain/s has to point to ingress IP 
#   ## this is a list object
#   # hosts: 
#   # - tudomin.io
  
##### OPTIONALend - ingress-evenodds.yaml

