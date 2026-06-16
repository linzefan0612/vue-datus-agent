import { shallowRef } from "vue";
import { setCurrentUser, request } from "@/lib/request";

/**
 * 用户信息接口
 */
export interface UserInfo {
  userId: number;
  username: string;
  realname: string;
  email: string;
  mobilePhone?: string;
  fixedPhone?: string;
  company?: string;
  department?: string;
  title?: string;
  userStatus?: string;
  sortNumber?: string;
  permissionList?: (string | null)[];
}

/**
 * 认证状态
 */
export interface AuthState {
  loading: boolean;
  authenticated: boolean;
  user: UserInfo | null;
}

// 认证配置从环境变量获取
const AUTH_ENABLED = import.meta.env.VITE_AUTH_ENABLED === "true";
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || "";
const AUTH_LOGIN_URL = import.meta.env.VITE_AUTH_LOGIN_URL || "";
const DEV_ACCESS_TOKEN = import.meta.env.VITE_DEV_ACCESS_TOKEN || "";

// 本地开发模式下的默认用户数据
const DEV_DEFAULT_USER: UserInfo = {
  userId: 1,
  username: "admin",
  realname: "系统管理员",
  email: "",
};

/**
 * 判断是否为本地开发环境
 * 通过 VITE_DEV_ACCESS_TOKEN 存在且为非空字符串来判断
 */
function isLocalDevelopment(): boolean {
  return import.meta.env.DEV && !DEV_ACCESS_TOKEN;
}

/**
 * 从 cookie 中获取 access_token
 */
function getAccessTokenFromCookie(): string | null {
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === "access_token") {
      return decodeURIComponent(value);
    }
  }
  return null;
}

/**
 * 获取 access_token
 * 优先使用环境变量中的测试 token（开发环境），其次使用 cookie 中的 token
 */
function getAccessToken(): string | null {
  // 优先使用环境变量中的测试 token
  if (DEV_ACCESS_TOKEN) {
    return DEV_ACCESS_TOKEN;
  }
  // 其次使用 cookie 中的 token
  return getAccessTokenFromCookie();
}

/**
 * 跳转到登录页
 */
function redirectToLogin(): void {
  if (AUTH_LOGIN_URL) {
    location.href = AUTH_LOGIN_URL;
  }
}

/**
 * 获取用户详情
 */
async function fetchUserInfo(token: string): Promise<UserInfo> {
  const response = await request(AUTH_API_URL, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return response.json();
}

/**
 * 认证 composable
 * 处理登录校验、用户信息获取等逻辑
 */
export function useAuth() {
  const state = shallowRef<AuthState>({
    loading: true,
    authenticated: false,
    user: null,
  });

  /**
   * 执行认证校验
   */
  async function checkAuth(): Promise<void> {
    state.value = { ...state.value, loading: true };

    // 认证未启用或本地开发环境，免鉴权，使用默认用户数据
    if (!AUTH_ENABLED || isLocalDevelopment()) {
      setCurrentUser(DEV_DEFAULT_USER);
      state.value = {
        loading: false,
        authenticated: true,
        user: DEV_DEFAULT_USER,
      };
      return;
    }

    try {
      // 获取 access_token（优先环境变量，其次 cookie）
      const token = getAccessToken();

      if (!token) {
        // token 为空，跳转登录页
        setCurrentUser(null);
        redirectToLogin();
        state.value = { loading: false, authenticated: false, user: null };
        return;
      }

      // 调用用户详情接口
      const result = await fetchUserInfo(token);

      // 判断是否认证成功：code 为 200 且 data 不为空
      if (result && Object.keys(result)?.length) {
        setCurrentUser(result);
        state.value = {
          loading: false,
          authenticated: true,
          user: result,
        };
      } else {
        // 认证失败，跳转登录页
        setCurrentUser(null);
        redirectToLogin();
        state.value = { loading: false, authenticated: false, user: null };
      }
    } catch (error) {
      console.error("认证校验失败:", error);
      // 发生错误，跳转登录页
      setCurrentUser(null);
      redirectToLogin();
      state.value = { loading: false, authenticated: false, user: null };
    }
  }

  return {
    state,
    checkAuth,
  };
}
