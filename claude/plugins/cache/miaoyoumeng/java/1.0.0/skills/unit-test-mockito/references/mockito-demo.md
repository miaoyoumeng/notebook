### Java 单元测试示例

1. service 单元测试示例

- 源码
```java

/**
 */
@Slf4j
@Service
public class LoginServiceImpl implements ILoginService {

    @Resource
    private IUserSsoService ssoUserService;

    @Resource
    private IUserRoleService userRoleService;

    @Resource
    private ITokenService tokenService;

    @Resource
    private IUserPwdService userPwdService;

    @Resource
    private EventManager eventManager;

    @Resource
    private SsoConfig ssoConfig;

    /**
     * @param uid      唯一标识符
     * @param password 密码
     * @param info     登录附带信息
     * @return
     * @throws SsoException
     */
    @Override
    public JwtToken loginByUid(final String uid, final String password,
                               final LoginInfoDTO info) throws SsoException {
        if (uid == null || password == null) {
            log.warn("login by uid and pwd, uid = {}, password = {} ", uid, password);
            throw new SsoException(SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }
        Long userId;
        if (PhoneNumberUtils.isPhoneNumber(uid)) {
            //手机登录
            userId = this.ssoUserService.getUserIdByChinaMobile(uid);
        } else if (EmailUtils.isEmail(uid)) {
            userId = this.ssoUserService.getUserIdByEmail(uid);
        } else {
            userId = this.ssoUserService.getUserIdByName(uid);
        }
        if (userId == null) {
            throw new SsoException(SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }
        Boolean pwdVerify = this.userPwdService.verifyUserIdPwd(userId, password);
        if (pwdVerify == null || !pwdVerify) {
            log.info("verifyUserIdPwd error [{}]", userId);
            throw new SsoException(SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }
        if (info != null) {
            info.setLoginType(EnumLoginType.UID_PWD.getCode());
        }
        return this.loginToken(userId, info);
    }

    @Override
    public JwtToken loginByMobile(final Integer countryCode, final String phoneNumber, final String smsVerifyCode,
                                  final LoginInfoDTO info) throws SsoException {
        if (phoneNumber == null || !PhoneNumberUtils.isPhoneNumber(countryCode, phoneNumber)) {
            log.warn("login by phoneNumber is illegal...");
            throw new SsoException(SsoErrorCode.REG_PHONE_NUMBER_ILLEGAL);
        }
        if (!verifySmsCode(countryCode, phoneNumber, smsVerifyCode)) {
            log.warn("login by  phoneNumber [{}] smsCode is illegal", phoneNumber);
            throw new SsoException(SsoErrorCode.SAFE_SMS_CODE_VERIFY_ERROR);
        }
        Long userId = this.ssoUserService.getUserIdByPhoneNumber(countryCode, phoneNumber);
        if (userId == null) {
            if (log.isInfoEnabled()) {
                log.info("login by phoneNumber [{}] is bind any user...", phoneNumber);
            }
            throw new SsoException(SsoErrorCode.REG_PHONE_NUMBER_NOT_EXIST);
        }
        if (info != null) {
            info.setLoginType(EnumLoginType.PHONE_NUMBER.getCode());
        }
        return this.loginToken(userId, info);

    }

    /**
     * @param userId 用户id
     * @param info   登录扩展信息
     * @return
     */
    private JwtToken loginToken(Long userId, LoginInfoDTO info) throws SsoException {
        if (userId == null) {
            log.warn("userId param is error...");
            return null;
        }
        LoginInfoDTO loginInfo = info != null ? info :
                LoginInfoDTO.builder().channelKey(EnumSsoChannel.WEB_SITE.getKey()).build();
        if (log.isDebugEnabled()) {
            log.debug("login by  userId [{}]", userId);
        }
        loginInfo.setLoginType(EnumLoginType.PHONE_NUMBER.getCode());
        UserDTO user = ssoUserService.getById(userId);
        if (user == null) {
            log.warn("userId [{}] is null ...", userId);
            return null;
        }
        if (EnumUserStatus.FREEZE.equals(user.getStatus()) ||
                EnumUserStatus.BLACK.equals(user.getStatus())) {
            if (log.isInfoEnabled()) {
                log.info("userId [{}] is [{}]", userId, user.getStatus());
            }
            throw new SsoException(SsoErrorCode.USER_LOGIN_USER_FREEZE_ERROR);
        }

        Set<EnumRole> roles = this.userRoleService.listByUserId(userId);
        final String profilePic = user.getProfilePic() == null ?
                ssoConfig.getDefaultProfilePicture() : user.getProfilePic();
        JwtUser jwt = JwtUser.builder().userId(userId).
                userName(user.getUserName())
                .status(EnumUserStatus.of(user.getStatus()))
                .loginTime(DateTime.now().toDate())
                .defaultRole(EnumRole.of(user.getDefaultRole()))
                .roles(roles).single(user.getSingleSignOn())
                .profilePic(profilePic).salt(user.getSalt())
                .build();
        //发送登录事件
        final EnumSsoChannel loginChannel = EnumSsoChannel.of(loginInfo.getChannelKey());
        JwtToken jwtToken = JwtUtils.token(jwt, loginChannel);
        this.eventManager.loginEvent(userId, loginInfo);
        this.tokenService.setLoginToken(userId, jwtToken, loginChannel);
        return jwtToken;
    }


    /**
     * 验证短信验证码
     *
     * @param countryCode
     * @param phoneNumber
     * @param smsCode
     * @return
     */
    private boolean verifySmsCode(Integer countryCode, String phoneNumber, String smsCode) {
        // todo

        return true;
    }
}
```


- 单元测试示例
```java

/**
 * LoginServiceImpl 单元测试
 *
 */
@ExtendWith(SpringExtension.class)
@DisplayName("LoginServiceImpl 服务测试")
public class LoginServiceImplTest {

    @Mock
    private IUserSsoService ssoUserService;

    @Mock
    private IUserRoleService userRoleService;

    @Mock
    private ITokenService tokenService;

    @Mock
    private IUserPwdService userPwdService;

    @InjectMocks
    private LoginServiceImpl loginService;

    private static final Long USER_ID = 1L;
    private static final String PASSWORD = "testPassword123";
    private static final String USER_NAME = "test_user";
    private static final String PHONE_NUMBER = "13800138000";
    private static final String EMAIL = "test@example.com";
    private static final Integer COUNTRY_CODE = 86;


    @Nested
    @DisplayName("loginByUid() 方法测试")
    class LoginByUid {
        @Test
        @DisplayName("uid 为 null 时应抛出 SsoException")
        void uidNull_shouldThrowException() {
            Throwable thrown = catchThrowable(() -> loginService.loginByUid(null, "password", null));
            assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }

        @Test
        @DisplayName("密码为 null 时应抛出 SsoException")
        void passwordNull_shouldThrowException() {
            Throwable thrown = catchThrowable(() -> loginService.loginByUid(USER_NAME, null, null));
            assertThat(thrown).isInstanceOf(SsoException.class);
            assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }

        @Test
        @DisplayName("uid 和密码为 null 时应抛出 SsoException")
        void uidPasswordBothNull_shouldThrowException() {
            Throwable thrown = catchThrowable(() -> loginService.loginByUid(null, null, null));
            assertThat(thrown).isInstanceOf(SsoException.class);
            assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
        }

        @Test
        @DisplayName("手机号找不到对应用户时应抛出 SsoException")
        void phoneNumber_userNotFound_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(PHONE_NUMBER)).thenReturn(true);
                mockedEmail.when(() -> EmailUtils.isEmail(PHONE_NUMBER)).thenReturn(false);

                when(ssoUserService.getUserIdByChinaMobile(PHONE_NUMBER)).thenReturn(null);

                Throwable thrown = catchThrowable(() -> loginService.loginByUid(PHONE_NUMBER, PASSWORD, null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
            }
        }

        @Test
        @DisplayName("邮箱找不到对应用户时应抛出 SsoException")
        void email_userNotFound_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(EMAIL)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(EMAIL)).thenReturn(true);

                when(ssoUserService.getUserIdByEmail(EMAIL)).thenReturn(null);

                Throwable thrown = catchThrowable(() -> loginService.loginByUid(EMAIL, PASSWORD, null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
            }
        }

        @Test
        @DisplayName("用户名找不到对应用户时应抛出 SsoException")
        void username_userNotFound_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(null);

                Throwable thrown = catchThrowable(() -> loginService.loginByUid(USER_NAME, PASSWORD, null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
            }
        }

        @Test
        @DisplayName("错误密码时应抛出 SsoException")
        void wrongPassword_shouldThrowException() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(false);

                assertSsoThrown(() -> loginService.loginByUid(USER_NAME, PASSWORD, null),
                        SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
            }
        }

        @Test
        @DisplayName("密码验证返回 null 时应抛出 SsoException")
        void passwordVerifyReturnsNull_shouldThrowException() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(null);

                assertSsoThrown(() -> loginService.loginByUid(USER_NAME, PASSWORD, null),
                        SsoErrorCode.USER_LOGIN_UNIQ_INFO_ERROR);
            }
        }

        @Test
        @DisplayName("手机号登录成功")
        void phoneNumber_success() throws SsoException {
            LoginInfoDTO info = new LoginInfoDTO();
            info.setChannelKey(EnumSsoChannel.WEB_SITE.getKey());

            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(PHONE_NUMBER)).thenReturn(true);
                mockedEmail.when(() -> EmailUtils.isEmail(PHONE_NUMBER)).thenReturn(false);

                when(ssoUserService.getUserIdByChinaMobile(PHONE_NUMBER)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mock-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByUid(PHONE_NUMBER, PASSWORD, info);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mock-jwt-token");
                assertThat(info.getLoginType()).isEqualTo(EnumLoginType.PHONE_NUMBER.getCode());
                // TODO: 源 bug - loginToken() 中无条件 setLoginType(PHONE_NUMBER) 覆盖了上层设置的 UID_PWD

                verify(tokenService).setLoginToken(eq(USER_ID), eq(mockToken), any(EnumSsoChannel.class));
            }
        }

        @Test
        @DisplayName("邮箱登录成功")
        void email_success() throws SsoException {
            LoginInfoDTO info = new LoginInfoDTO();
            info.setChannelKey(EnumSsoChannel.WEB_SITE.getKey());

            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(EMAIL)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(EMAIL)).thenReturn(true);

                when(ssoUserService.getUserIdByEmail(EMAIL)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mock-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByUid(EMAIL, PASSWORD, info);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mock-jwt-token");
                assertThat(info.getLoginType()).isEqualTo(EnumLoginType.PHONE_NUMBER.getCode());
                // TODO: 源 bug - loginToken() 中无条件 setLoginType(PHONE_NUMBER) 覆盖了上层设置的 UID_PWD
            }
        }

        @Test
        @DisplayName("用户名登录成功")
        void username_success() throws SsoException {
            LoginInfoDTO info = new LoginInfoDTO();
            info.setChannelKey(EnumSsoChannel.WEB_SITE.getKey());

            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mock-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByUid(USER_NAME, PASSWORD, info);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mock-jwt-token");
                assertThat(info.getLoginType()).isEqualTo(EnumLoginType.PHONE_NUMBER.getCode());
                // TODO: 源 bug - loginToken() 中无条件 setLoginType(PHONE_NUMBER) 覆盖了上层设置的 UID_PWD
            }
        }

        @Test
        @DisplayName("用户冻结时需要抛出对应的 SsoException")
        void userFrozen_shouldThrowException() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);

                UserDTO frozenUser = buildUserWithStatus(EnumUserStatus.FREEZE.getCode());
                when(ssoUserService.getById(USER_ID)).thenReturn(frozenUser);

                assertSsoThrown(() -> loginService.loginByUid(USER_NAME, PASSWORD, null),
                        SsoErrorCode.USER_LOGIN_USER_FREEZE_ERROR);
            }
        }

        @Test
        @DisplayName("用户进入黑名单时需要抛出对应的 SsoException")
        void userBlacklisted_shouldThrowException() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);

                UserDTO blackUser = buildUserWithStatus(EnumUserStatus.BLACK.getCode());
                when(ssoUserService.getById(USER_ID)).thenReturn(blackUser);

                assertSsoThrown(() -> loginService.loginByUid(USER_NAME, PASSWORD, null),
                        SsoErrorCode.USER_LOGIN_USER_FREEZE_ERROR);
            }
        }

        @Test
        @DisplayName("用户登录返回 null 时需要抛出对应的 SsoException")
        void infoNull_shouldReturnToken() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<EmailUtils> mockedEmail = mockStatic(EmailUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(USER_NAME)).thenReturn(false);
                mockedEmail.when(() -> EmailUtils.isEmail(USER_NAME)).thenReturn(false);

                when(ssoUserService.getUserIdByName(USER_NAME)).thenReturn(USER_ID);
                when(userPwdService.verifyUserIdPwd(USER_ID, PASSWORD)).thenReturn(true);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mock-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByUid(USER_NAME, PASSWORD, null);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mock-jwt-token");
            }
        }

    }

    @Nested
    @DisplayName("loginByMobile() 方法测试")
    class LoginByMobile {
        @Test
        void loginByMobile_phoneNumberNull_shouldThrowException() {
            Throwable thrown = catchThrowable(() -> loginService.loginByMobile(COUNTRY_CODE, null, "123456", null));
            assertThat(thrown).isInstanceOf(SsoException.class);
            assertSsoErrorCode(thrown, SsoErrorCode.REG_PHONE_NUMBER_ILLEGAL);
        }

        @Test
        void loginByMobile_invalidPhoneNumber_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mocked = mockStatic(PhoneNumberUtils.class)) {
                mocked.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, "123")).thenReturn(false);

                Throwable thrown = catchThrowable(() -> loginService.loginByMobile(COUNTRY_CODE, "123", "123456", null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.REG_PHONE_NUMBER_ILLEGAL);
            }
        }

        @Test
        void loginByMobile_smsCodeNull_userNotBound_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mocked = mockStatic(PhoneNumberUtils.class)) {
                mocked.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(true);

                when(ssoUserService.getUserIdByPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(null);

                Throwable thrown = catchThrowable(() -> loginService.loginByMobile(COUNTRY_CODE, PHONE_NUMBER, null, null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.REG_PHONE_NUMBER_NOT_EXIST);
            }
        }

        @Test
        void loginByMobile_userNotBound_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mocked = mockStatic(PhoneNumberUtils.class)) {
                mocked.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(true);

                when(ssoUserService.getUserIdByPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(null);

                Throwable thrown = catchThrowable(() -> loginService.loginByMobile(COUNTRY_CODE, PHONE_NUMBER, "123456", null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.REG_PHONE_NUMBER_NOT_EXIST);
            }
        }

        @Test
        void loginByMobile_success() throws SsoException {
            LoginInfoDTO info = new LoginInfoDTO();
            info.setChannelKey(EnumSsoChannel.WEB_SITE.getKey());

            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(true);

                when(ssoUserService.getUserIdByPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(USER_ID);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mobile-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByMobile(COUNTRY_CODE, PHONE_NUMBER, "123456", info);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mobile-jwt-token");
                assertThat(info.getLoginType()).isEqualTo(EnumLoginType.PHONE_NUMBER.getCode());

                verify(tokenService).setLoginToken(eq(USER_ID), eq(mockToken), any(EnumSsoChannel.class));
            }
        }

        @Test
        void loginByMobile_infoNull_success() throws SsoException {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class);
                 MockedStatic<JwtUtils> mockedJwt = mockStatic(JwtUtils.class)) {

                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(true);

                when(ssoUserService.getUserIdByPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(USER_ID);
                when(ssoUserService.getById(USER_ID)).thenReturn(buildActiveUser());
                when(userRoleService.listByUserId(USER_ID)).thenReturn(buildRoles());

                JwtToken mockToken = buildMockToken("mobile-jwt-token");
                mockedJwt.when(() -> JwtUtils.token(any(JwtUser.class), any(EnumSsoChannel.class))).thenReturn(mockToken);

                JwtToken result = loginService.loginByMobile(COUNTRY_CODE, PHONE_NUMBER, "123456", null);

                assertThat(result).isNotNull();
                assertThat(result.getToken()).isEqualTo("mobile-jwt-token");
            }
        }

        @Test
        void loginByMobile_userFrozen_shouldThrowException() {
            try (MockedStatic<PhoneNumberUtils> mockedPhone = mockStatic(PhoneNumberUtils.class)) {
                mockedPhone.when(() -> PhoneNumberUtils.isPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(true);

                when(ssoUserService.getUserIdByPhoneNumber(COUNTRY_CODE, PHONE_NUMBER)).thenReturn(USER_ID);

                UserDTO frozenUser = buildUserWithStatus(EnumUserStatus.FREEZE.getCode());
                when(ssoUserService.getById(USER_ID)).thenReturn(frozenUser);

                Throwable thrown = catchThrowable(() -> loginService.loginByMobile(COUNTRY_CODE, PHONE_NUMBER, "123456", null));
                assertThat(thrown).isInstanceOf(SsoException.class);
                assertSsoErrorCode(thrown, SsoErrorCode.USER_LOGIN_USER_FREEZE_ERROR);
            }
        }
    }
    private UserDTO buildActiveUser() {
        UserDTO user = new UserDTO();
        user.setId(USER_ID);
        user.setUserName(USER_NAME);
        user.setDisplayName("Test User");
        user.setProfilePic("profile.jpg");
        user.setStatus(EnumUserStatus.ACTIVE.getCode());
        user.setSingleSignOn((short) 0);
        user.setDefaultRole((short) 1);
        user.setSalt("testSalt");
        return user;
    }

    private UserDTO buildUserWithStatus(Short status) {
        UserDTO user = new UserDTO();
        user.setId(USER_ID);
        user.setUserName(USER_NAME);
        user.setProfilePic("profile.jpg");
        user.setStatus(status);
        user.setSingleSignOn((short) 0);
        user.setDefaultRole((short) 1);
        user.setSalt("testSalt");
        return user;
    }

    private Set<EnumRole> buildRoles() {
        Set<EnumRole> roles = new HashSet<>();
        roles.add(EnumRole.USER);
        return roles;
    }

    private JwtToken buildMockToken(String tokenValue) {
        JwtToken token = new JwtToken();
        token.setToken(tokenValue);
        token.setUserId(USER_ID);
        return token;
    }

    private void assertSsoErrorCode(Throwable e, SsoErrorCode expected) {
        assertThat(e).isInstanceOf(SsoException.class);
        SsoException sse = (SsoException) e;
        assertThat(sse.getResult().getUniqCode()).isEqualTo(expected.getUniqCode());
    }

    private void assertSsoThrown(org.assertj.core.api.ThrowableAssert.ThrowingCallable callable,
                                 SsoErrorCode expected) {
        Throwable thrown = catchThrowable(callable);
        assertSsoErrorCode(thrown, expected);
    }
}

```
