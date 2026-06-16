import { computed, shallowRef } from "vue";

export type AppRoute = "app" | "login" | "callback";

const currentPath = shallowRef(window.location.pathname);

window.addEventListener("popstate", () => {
  currentPath.value = window.location.pathname;
});

export function useRouter() {
  const currentRoute = computed<AppRoute>(() => {
    const path = currentPath.value;
    if (path === "/login") return "login";
    if (path === "/callback") return "callback";
    return "app";
  });

  function navigate(path: string) {
    window.history.pushState(null, "", path);
    currentPath.value = path;
  }

  return { currentRoute, navigate };
}
