1、maven化项目，执行mvn clean deploy 即可。

东方优播标准[settings](http://dfub-doc.test.xdf.cn/attachment/settings.xml)

2、非maven化项目只需如下命令上传jar包。

2.1、上传编译后的class jar包（releases）
```
mvn deploy:deploy-file -Dfile=${包文件相对路径} -DgroupId=cn.dfub \
-DartifactId=${jar包artifactId名称} -Dversion=${jar包版本号} \
-Dpackaging=jar \
-Durl=http://dfubnexus.test.xdf.cn/repository/maven-releases/ \
-DrepositoryId=releases
```
2.2、上传Java源代码jar包（releases）
```
mvn deploy:deploy-file -Dfile=${包文件相对路径} -DgroupId=cn.dfub \
-DartifactId=${jar包artifactId名称} -Dversion=${jar包版本号} \
-Dpackaging=jar -Dclassifier=sources \
-Durl=http://dfubnexus.test.xdf.cn/repository/maven-releases/ \
-DrepositoryId=releases
```
 

2.3、上传编译后的class jar包到快照仓库（snapshots）

```
mvn deploy:deploy-file -Dfile=${包文件相对路径} -DgroupId=cn.dfub \
-DartifactId=${jar包artifactId名称} -Dversion=${jar包版本号}-SNAPSHOT -Dpackaging=jar \
-Durl=http://dfubnexus.test.xdf.cn/repository/maven-snapshots/ \
-DrepositoryId=snapshots
```
