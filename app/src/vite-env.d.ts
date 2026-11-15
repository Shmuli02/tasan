/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TASAN_PROXY_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module "*.geojson" {
  const value: unknown;
  export default value;
}
