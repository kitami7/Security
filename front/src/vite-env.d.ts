/// <reference types="vite/client" />

// 環境変数の型定義
interface ImportMetaEnv {
    readonly VITE_API_URL: string;
}

// 環境変数を使用するための型定義
// Viteの環境変数はすべて`import.meta.env`オブジェクトに格納されます。
interface ImportMeta {
    readonly env: ImportMetaEnv;
}