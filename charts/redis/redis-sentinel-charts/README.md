
#### 安装

```

    helm install ${appName} --generate-name -n miaoyoumeng1

    helm install ${appName} ${charts_path} -n ${namespace}

    helm install redis redis-sentinel-charts  -n miaoyoumeng1


```

#### 卸载

```

helm install ${appName} -n ${namespace}

helm uninstall redis  -n miaoyoumeng1


```