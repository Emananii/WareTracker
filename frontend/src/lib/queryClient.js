import { QueryClient } from "@tanstack/react-query";
import { BASE_URL } from "./constants";

// Internal error helper
async function throwIfResNotOk(res) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

// Generic API request wrapper (used for POST, PUT, DELETE, etc.)
export async function apiRequest(method, url, data) {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    // Removed credentials: "include"
  });

  await throwIfResNotOk(res);
  return res;
}

// Query fetch function (used for GET queries via React Query)
export function getQueryFn({ on401 }) {
  return async ({ queryKey }) => {
    const res = await fetch(queryKey[0]); // Removed credentials: "include"

    if (on401 === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };
}

// Default React Query configuration
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

