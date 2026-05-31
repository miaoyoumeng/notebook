# CI 集成指南

GitHub Actions + Maven 的 TDD CI 配置。

---

## 前提条件

- Java 17+
- Maven 3.8+
- GitHub Actions

---

## 完整 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: testdb
        ports:
          - 3306:3306
        options: >-
          --health-cmd "mysqladmin ping -h localhost"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Build with Maven
        run: mvn --batch-mode compile

      - name: Unit Tests
        run: mvn --batch-mode test

      - name: Integration Tests
        run: mvn --batch-mode verify -Dskip.unit.tests=true
        env:
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/testdb
          SPRING_DATASOURCE_USERNAME: root
          SPRING_DATASOURCE_PASSWORD: root
          SPRING_REDIS_HOST: localhost
          SPRING_REDIS_PORT: 6379

      - name: Generate JaCoCo Report
        run: mvn jacoco:report
        if: always()

      - name: Upload Coverage Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: jacoco-report
          path: target/site/jacoco/

      - name: Coverage Gate
        uses: cicirello/jacoco-badge-generator@v2
        with:
          jacoco-csv-file: target/site/jacoco/jacoco.csv
          generate-coverage-badge: true
          coverage-label: 'line coverage'
```

---

## 质量门控

```xml
<!-- pom.xml JaCoCo 覆盖率检查 -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <executions>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>PACKAGE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.75</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

构建时如果覆盖率不满足阈值，`mvn verify` 会失败。

---

## TDD 预提交检查

```yaml
# .github/workflows/pre-commit.yml
name: Pre-Commit TDD Check

on:
  push:
    branches-ignore: [main]

jobs:
  tdd-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: 'maven'

      - name: Verify Tests Exist for Changes
        run: |
          # 检查新增/修改的 java 文件是否有对应测试
          for file in $(git diff --name-only origin/main..HEAD -- 'src/main/java/**/*.java'); do
            test_file=$(echo "$file" | sed 's|src/main|src/test|' | sed 's|\.java$|Test.java|')
            if [ ! -f "$test_file" ] && [ ! -f "${test_file/Test.java/IT.java}" ]; then
              echo "WARNING: No test found for $file"
              echo "Expected: $test_file or ${test_file/Test.java/IT.java}"
            fi
          done

      - name: Run All Tests
        run: mvn --batch-mode verify
```

---

## 本地开发工作流命令

```bash
# RED 阶段：写测试，看它失败
mvn test -Dtest=UserServiceTest

# GREEN 阶段：写实现，看它通过
mvn test -Dtest=UserServiceTest

# 验证所有测试通过
mvn test

# 验证集成测试
mvn verify

# 生成覆盖率报告
mvn clean test jacoco:report
open target/site/jacoco/index.html

# 提交
git add src/test/java/.../UserServiceTest.java
git add src/main/java/.../UserServiceImpl.java
git commit -m "feat: add user query by id with cache"
```
