# PRACTICA Final - Contenedores: más que VMs 

## Kubernetes

Sección relacionada con Kubernetes y sus manifiestos de la práctica final del módulo `Contenedores: más que VMs`


## Índice:
- [Objetivos](#objetivos)
- [Pasos para ejecutar el stack](#pasos-para-ejecutar-el-stack)
- [Comprobar el despliegue](#comprobar-el-despliegue)
- [Manifiestos](#manifiestos)
    - [Deployment](#deployment)
    - [Statefullset](#statefullset)
    - [Configmaps y Secrets](#configmaps-y-secrets)
    - [Services:](#services)
    - [ClusterIssuer](#clusterIssuer)
    - [Ingress](#ingress)
    - [Autoescalado](#autoescalado)
    - [ECK](#sistema-de-logs-con-eck)
    - [Ingress](#ingress)


## Objetivos

En esta sección se cubren los siguientes puntos de la práctica relacionados con manifiestos de Kubernetes: 7, 9-17 y 19.

En esta parte de la práctica los valores configurables son:
- Se puede actuar en la configuración de Postgres modificando los archivos del [configmap](#ddbb-configmap  yaml)
- los configurados en el [secrect](#ddbb-secret-evenoddsyaml) para la base de datos.
- los configurados en [app_configmap.yaml](#app_configmapyaml)

## Pasos para ejecutar el stack

Para ejecutar el repo completamente en un cluster limpio y se debe ejecutar los siguientes pasos:

1. Situarse en el directorio raíz del repositorio

2. Para crear el namespace utilizado en los scripts ejecuta:

    `kubectl apply -f initial_scripts/namespace.yaml` 

3. Para una completa funcionalidad del proyecto es necesario tener instalados los siguientes controladores y operadores antes de seguir la instalación:
    - **Cert-manager**:

        Para la generación de certificados con Let's Encrypt

        En caso de que no esté instalado en el cluster es necesario instalarlo ejecuta:
        
        `kubectl apply -f initial_scripts/cert_manager`
    
    - **Nginx ingress controller**:

        Si bien los objetos ingress son parte del API de kubernetes es necesario instalar un operador externo que de funcionalidad a los objetos ingress.
        
        Si no está instalado se puede instalar con:
        
        `kubectl apply -f initial_scripts/nginx_ingress_controller`

    - **ECK operator**:

        Para la gestión de logs.

        En caso de que no esté instalado en el cluster ejecuta: 
        
        `kubectl apply -f initial_scripts/eck_operator`



4. Una vez hecho esto se pueden ejecutar todos los manifiestos del directorio raíz con el siguiente comando `kubectl apply -f .`

    Esto instala la aplicación:
    - Un deployment para la app: 
        `app_deployment.yaml`: 
        Contiene un initContainer para asegurarse de que la base de datos está operativa antes de arrancar la aplicación.

    - Un statefullset para la base de datos y su PVC para persistencia de datos: 
        `ddbb_deployment.yaml`

    - Los configmaps y secrets necesarios:
        1. `app_configmap.yaml`
        2. `ddbb-configmap.yaml`
        3. `ddbb-secret-evenodds.yaml`

    - Los services necesarios:
        1. `ddbb-headless.yaml`
        2. `service-app-ddbb.yaml`
        3. `service-evenodds.yaml`

    - Un clusterIssuer para pedir un certificado de Let's Encript:
        `clusterissuer-letsencrypt.yaml`

    - Autoescalado:
        `autoescale.yaml`

    - Sistema de logs con ECK:
        1. `eck_2.4.0_cluster_deploy.yaml`
        2. `eck_2.4.0_kibana.yaml`
        3. `eck_2.4.0_filebeat.yaml`
        4. `eck_2.4.0_metricbeat.yaml`

5. Para crear el ingress ejecutar `kubectl apply -f ingress/ingress.yaml` pero antes es necesario conocer la IP pública del ingress controller.
    
    El ingress solicita un certificado y es necesario configurar el host.

    Se puede editar el fichero `ingress/ingress.yaml` con el siguiente comando antes de desplegar el manifiesto:

    `DNS_IP_HOST=$(kubectl get -n ingress-nginx services | grep ingress-nginx-controller | awk '{print $4}' | grep -v none); sed -i "s/IP/$(echo $DNS_IP_HOST)/" ingress/ingress.yaml`

    Una vez ejecutado se puede comprobar si se ha configurado correctamente el host en el fichero y desplegar ejecutando:

    `kubectl apply -f ingress/ingress.yaml`

## Comprobar el despliegue
Para comprobar el despliegue en caso de que se configure el ingress se puede obtener el enlace de acceso con este comando:
Se pueden obtener las URLs (con y sin https) con este comando:
`INGRESS=$(kubectl get ingress -n evenodds-ns | grep evenodds-ingress | awk '{print $3}') && echo http://$INGRESS && echo https://$INGRESS`
![Captura desde 2022-10-02 12-18-12](https://user-images.githubusercontent.com/2046110/193449195-b87229a5-9472-43f1-9668-ee32ba7c8958.png)

En caso de no usar ingress se puede acceder con este comando:
Se pueden obtener las URLs (con y sin https) con este comando:
`LB=$(kubectl get service -n evenodds-ns | grep evenodds-lb | awk '{print $4}') && echo http://$LB`

![Captura desde 2022-10-02 12-18-13](https://user-images.githubusercontent.com/2046110/193449194-85f0f874-cd82-4336-828e-141e3000feca.png)


## Manifiestos


La aplicación está compuesta de los siguientes manifiestos:

### Deployment 
#### app_deployment.yaml: 

Carga variables de entorno con información de la base de datos para conectar con la base de datos. Estos datos son leidos desde el sercret de la base de datos.

También obtiene como variables de entorno configuraciones como el puerto de la aplicación y configuraciones relacionada con la rotación de logs desde el configmap definido en `app_configmap.yaml`

Está configurada con podantiaffinity para que si es posible un nuevo pod no se instale en el mismo nodo que otro pod activo de la aplicación.

La aplicación genera logs en formato json tanto en stdout y stderr como a ficheros

### Statefullset
#### ddbb_deployment.yaml:

Para la base de datos. Incluye su PVC para persistencia de datos

Tiene PodAffinity para que si es posible se instale junto a los pod de aplicación.

Obtiene los datos de configuración del secret `evenodds-db-secret`

Carga configuraciones para postgres desde dos configmap.

### Configmaps y Secrets:

#### app_configmap.yaml

Pasa información a la aplicación como el host de la base de datos y el puerto asi como información de la configuración de rotación de logs.

#### ddbb-configmap.yaml

Contiene dos archivos de configuración para aplicar a la imagen de postgres.

#### ddbb-secret-evenodds.yaml

Desde este fichero se facilitan los datos de configuración de la base de datos.

Esta es la plantilla:

    apiVersion: v1
    kind: Secret
    metadata:
    name: evenodds-db-secret
    namespace: evenodds-ns
    type: Opaque
    data:
    POSTGRES_DB: cG9zdGdyZXM=
    POSTGRES_USER: cG9zdGdyZXM=
    POSTGRES_PASSWORD: cG9zdGdyZXM=

Los valores para POSTGRES_DB, POSTGRES_USER y POSTGRES_PASSWORD deben estar en base 64.

Los valores que quieras utilizar se pueden traducir con este comando:
` read -p "Dime una cadena de texto para pasar a base64: " STR; echo -n "$STR" | base64`

Por defecto se usa `postgres`

### Services:

#### ddbb-headless.yaml

Servicio headless para el tráfico interno de la base de datos.

#### service-app-ddbb.yaml

Servicio ClusterIP para la comunicación entre la aplicación y la base de datos.

#### service-evenodds.yaml

Servicio público como LoadBalancer para el acceso a la aplicación.

Puede obtenerse un enlace web para acceder a la aplicación con el siguiente comando:
`echo http://$(kubectl get -n evenodds-ns services | grep evenodds-lb | awk '{print $4}')`

### ClusterIssuer

#### clusterissuer-letsencrypt.yaml

Para pedir un certificado de Let's Encript.

Para que se haga efectivamente una solicitud del certificado es necesario ejecutar el ingress.

### Ingress
#### ingres/ingres.yaml

Solicita un certificado staging de Let's Enrypt al desplegarse.

Antes de ejecutarlo es necesario definir el host para que se pueda solicitar el certificado.

El archiov se puede configurar con este comando:
`DNS_IP_HOST=$(k get services -n ingress-nginx ingress-nginx-controller | tail -1 | awk '{print $4}'); sed -i "s/IP/$(echo $DNS_IP_HOST)/" ingress/ingress.yaml`

Una vez configurado se despliega:
`kubectl apply -f ingress/ingress.yaml`

Se pueden obtener las URLs (con y sin https) con este comando:
`INGRESS=$(kubectl get ingress -n evenodds-ns | grep evenodds-ingress | awk '{print $3}') && echo http://$INGRESS && echo https://$INGRESS`

Es posible que haya que esperar hasta que el certificado esté operativo.

Se puede revisar el estado de la solicitud del certificado con este comando:
`kubectl get certificaterequests.cert-manager.io -n evenodds-ns`

### Autoescalado
#### autoescale.yaml

Configura un sistema de auto escalado.



### Sistema de logs con ECK:
Es necesario que previamente esté instalado el operador de ECK: 

https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-installing-eck.html

#### eck_2.4.0_cluster_deploy.yaml
#### eck_2.4.0_kibana.yaml
#### eck_2.4.0_filebeat.yaml
#### eck_2.4.0_metricbeat.yaml

Una vez instalados el operador y estos cuatro manifiestos para acceder al backend de kibana ejecuta los siguientes comando.

Con este se obtiene la contraseña de aceso al panel:
`kubectl get secret -n evenodds-ns  eck-deploy-es-elastic-user -o=jsonpath='{.data.elastic}' | base64 --decode; echo`

Este comando genera la URL del panel:
`echo https://$(kubectl get services -n evenodds-ns | grep eck-deploy-kb-http | awk '{print $4}'):5601`


### Ingress:
#### ingress/ingress.yaml

Comentado más arriba, es necesario modificar el host en este archivo para configurar un host que apunte a la IP del ingress controller. Se puede utilizar este comando para obtener esa IP y configurar correctamente el fichero inicial (utilizando el servicio nip.io):
`DNS_IP_HOST=$(kubectl get -n ingress-nginx services | grep ingress-nginx-controller | awk '{print $4}' | grep -v none); sed -i "s/IP/$(echo $DNS_IP_HOST)/" ingress/ingress.yaml`

Para otra configuración modifica el archivo añadiendo el host final manualmente en los campos:
- spec.tls.hosts:
- spec.rules.host:


