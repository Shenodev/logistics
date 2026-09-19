export default defineNuxtRouteMiddleware((to) => {
  if (to.path === '/login' || to.path === '/signup') return
  if (to.path.startsWith('/admin')) {
    setPageLayout('admin')
    return
  }

  setPageLayout(portalToLayout(useAppRole()))
})