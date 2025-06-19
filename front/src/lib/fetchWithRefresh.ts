// src/lib/fetchWithRefresh.ts
let isRefreshing = false;
let failedQueue: {
  resolve: (token: any) => void;
  reject: (error: any) => void;
}[] = [];

const processQueue = (error: any, token: any = null) => {
  failedQueue.forEach(p => {
    if (error) {
      p.reject(error);
    } else {
      p.resolve(token);
    }
  });
  failedQueue = [];
};

export const fetchWithRefresh = async <T>(
  fetcher: () => Promise<{ data?: T; error?: any }>
): Promise<T> => {
  const res = await fetcher();

  if (res.error?.status === 401) {
    if (isRefreshing) {
      // 既にリフレッシュ中なら待つ
      return new Promise<T>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => fetcher().then(r => {
        if (r.data) return r.data;
        throw r.error ?? new Error("再試行でエラー");
      }));
    }

    isRefreshing = true;
    try {
      const refreshRes = await fetch("http://localhost:8000/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (refreshRes.ok) {
        processQueue(null);
        const retryRes = await fetcher();
        if (retryRes.data) return retryRes.data;
        throw retryRes.error ?? new Error("再試行でエラー");
      } else {
        processQueue(new Error("リフレッシュ失敗"));
        window.location.href = "/login";
        throw new Error("リフレッシュに失敗しました");
      }
    } catch (err) {
      processQueue(err);
      window.location.href = "/login";
      throw err;
    } finally {
      isRefreshing = false;
    }
  }

  if (res.data) return res.data;

  throw new Error(res.error?.message ?? "APIエラー");
};
