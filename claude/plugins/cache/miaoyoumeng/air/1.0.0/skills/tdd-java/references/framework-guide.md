# Java + Spring Boot 测试框架指南

本文档介绍 Java 17 + Spring Boot + JUnit 5 + Mockito 技术栈的测试实践。

---

## Service 层测试（纯 Mockito 单元测试）

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class UserServiceImplTest {

    @Mock
    private UserMapper userMapper;

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void shouldReturnUser_whenIdExists() {
        UserDO user = buildUser(1L, "Alice");
        when(userMapper.selectById(1L)).thenReturn(user);

        UserDTO result = userService.getById(1L);

        assertThat(result.getName()).isEqualTo("Alice");
        assertThat(result.getEmail()).isEqualTo("alice@example.com");
    }

    @Test
    void shouldThrowException_whenIdNotFound() {
        when(userMapper.selectById(999L)).thenReturn(null);

        assertThatThrownBy(() -> userService.getById(999L))
            .isInstanceOf(NotFoundException.class)
            .hasMessageContaining("999");
    }

    @Test
    void shouldCacheUserAfterQuery_whenFirstCall() {
        UserDO user = buildUser(1L, "Alice");
        ValueOperations<String, Object> ops = mock(ValueOperations.class);
        when(redisTemplate.opsForValue()).thenReturn(ops);
        when(userMapper.selectById(1L)).thenReturn(user);
        when(ops.get("user:1")).thenReturn(null);

        userService.getById(1L);

        verify(ops).set(eq("user:1"), any(UserDTO.class), any(Duration.class));
    }

    private UserDO buildUser(Long id, String name) {
        UserDO user = new UserDO();
        user.setId(id);
        user.setName(name);
        user.setEmail(name.toLowerCase() + "@example.com");
        return user;
    }
}
```

---

## Controller 层单元测试（MockMvc）

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private IUserService userService;

    @Test
    void shouldReturnUser_whenGetById() throws Exception {
        UserDTO user = new UserDTO(1L, "Alice", "alice@example.com");
        when(userService.getById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.name").value("Alice"))
            .andExpect(jsonPath("$.data.email").value("alice@example.com"));
    }

    @Test
    void shouldReturn404_whenUserNotFound() throws Exception {
        when(userService.getById(999L))
            .thenThrow(new NotFoundException("User not found: 999"));

        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound());
    }
}
```

---

## 集成测试（Spring Boot Test）

```java
// UserServiceImplIT.java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@Transactional  // 自动回滚，不留脏数据
class UserServiceImplIT {

    @Autowired
    private IUserService userService;

    @Autowired
    private UserMapper userMapper;

    @Test
    void shouldCreateAndQueryUser() {
        UserDTO input = new UserDTO("Bob", "bob@example.com");
        Long userId = userService.create(input);

        UserDTO result = userService.getById(userId);
        assertThat(result.getName()).isEqualTo("Bob");
    }

    @Test
    void shouldThrowException_whenDuplicateEmail() {
        userService.create(new UserDTO("Alice", "alice@example.com"));

        assertThatThrownBy(() ->
            userService.create(new UserDTO("Bob", "alice@example.com"))
        ).isInstanceOf(DuplicateEmailException.class);
    }
}
```

---

## Mapper 测试

```java
// UserMapperIT.java
import org.junit.jupiter.api.Test;
import org.mybatis.spring.boot.test.autoconfigure.MybatisTest;
import org.springframework.beans.factory.annotation.Autowired;

@MybatisTest
class UserMapperIT {

    @Autowired
    private UserMapper userMapper;

    @Test
    void shouldInsertAndSelectById() {
        UserDO user = new UserDO();
        user.setName("TestUser");
        user.setEmail("test@example.com");
        userMapper.insert(user);

        UserDO result = userMapper.selectById(user.getId());
        assertThat(result.getName()).isEqualTo("TestUser");
    }

    @Test
    void shouldReturnNull_whenIdNotExists() {
        UserDO result = userMapper.selectById(999999L);
        assertThat(result).isNull();
    }

    @Test
    void shouldSelectByEmail() {
        UserDO user = new UserDO();
        user.setEmail("unique@example.com");
        userMapper.insert(user);

        UserDO result = userMapper.selectByEmail("unique@example.com");
        assertThat(result).isNotNull();
    }
}
```

---

## Redis 测试

```java
// RedisCacheIT.java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.redis.DataRedisTest;

@DataRedisTest
class RedisCacheIT {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Test
    void shouldSetAndGetValue() {
        redisTemplate.opsForValue().set("test-key", "test-value", Duration.ofMinutes(1));

        Object result = redisTemplate.opsForValue().get("test-key");
        assertThat(result).isEqualTo("test-value");
    }

    @Test
    void shouldReturnNull_whenKeyExpired() throws InterruptedException {
        redisTemplate.opsForValue().set("expire-key", "value", Duration.ofMillis(100));

        Thread.sleep(150);

        assertThat(redisTemplate.opsForValue().get("expire-key")).isNull();
    }
}
```

---

## Testcontainers 集成测试（真实 Redis/MySQL）

```java
// UserServiceContainerIT.java
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.containers.MySQLContainer;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

@SpringBootTest
@Testcontainers
class UserServiceContainerIT {

    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Container
    static GenericContainer<?> redis = new GenericContainer<>(
        DockerImageName.parse("redis:7-alpine"))
        .withExposedPorts(6379);

    // Spring 动态属性会自动注入容器端口
    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
        registry.add("spring.redis.host", redis::getHost);
        registry.add("spring.redis.port", () -> redis.getMappedPort(6379));
    }

    @Test
    void shouldWorkWithRealInfrastructure() {
        // 使用真实 MySQL + Redis 的完整集成测试
    }
}
```

---

## 测试数据管理

### 程序插入数据（推荐方式）

```java
// 在测试中通过代码插入，不依赖数据库已有数据
@BeforeEach
void setUp() {
    userMapper.insert(new UserDO("test1", "test1@example.com"));
    userMapper.insert(new UserDO("test2", "test2@example.com"));
}
```

### SQL 初始化脚本

```sql
-- src/test/resources/test-data.sql
INSERT INTO user (name, email) VALUES ('init_user', 'init@example.com');
```

### 测试数据前缀标识

```java
// 用明确前缀区分测试数据
private static final String TEST_PREFIX = "TDD_TEST_";

@Test
void shouldDeleteUser() {
    userService.create(new UserDTO(TEST_PREFIX + "Alice", TEST_PREFIX + "alice@test.com"));
    // ...
}
```

---

## 常用 Mockito 模式

```java
// Stubbing
when(mapper.selectById(anyLong())).thenReturn(mockUser);

// Void 方法
doNothing().when(redisTemplate).delete(anyString());

// 抛异常
when(mapper.insert(any())).thenThrow(new DataAccessException("DB error"));

// ArgumentCaptor
ArgumentCaptor<UserDO> captor = ArgumentCaptor.forClass(UserDO.class);
verify(mapper).insert(captor.capture());
assertThat(captor.getValue().getName()).isEqualTo("Alice");

// 调用顺序
InOrder inOrder = inOrder(mapper, redisTemplate);
inOrder.verify(mapper).deleteById(1L);
inOrder.verify(redisTemplate).delete("user:1");

// Spy（部分 mock）
@Spy
private UserServiceImpl userService;
doReturn(cachedValue).when(userService).fetchFromRemote(anyLong());
```

---

## 测试命令速查

```bash
# 运行所有单元测试 (*Test.java)
mvn test

# 运行所有测试（含集成 *IT.java）
mvn verify

# 运行单个测试类
mvn test -Dtest=UserServiceTest

# 运行单个测试方法
mvn test -Dtest=UserServiceTest#shouldReturnUser_whenIdExists

# 跳过测试
mvn package -DskipTests

# 生成覆盖率报告
mvn clean test jacoco:report
# 报告位置: target/site/jacoco/index.html
```
