export default defineNuxtRouteMiddleware((to) => {
  if (to.path === '/login' || to.path === '/signup') return

  setPageLayout(portalToLayout(useAppRole()))
})