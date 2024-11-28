interface AppConfig {
  apiBaseUrl: string;
}

// 从 window._APP_CONFIG_ 获取运行时配置
declare global {
  interface Window {
    _APP_CONFIG_?: Partial<AppConfig>;
  }
}

// 默认配置
const defaultConfig: AppConfig = {
  apiBaseUrl: window._APP_CONFIG_?.apiBaseUrl || import.meta.env.VITE_API_BASE_URL || 'http://localhost:17778'
};

// 合并默认配置和运行时配置
export const getConfig = (): AppConfig => {
  return {
    ...defaultConfig,
    ...window._APP_CONFIG_
  };
}; 