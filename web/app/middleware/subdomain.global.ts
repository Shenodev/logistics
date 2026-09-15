export default defineNuxtRouteMiddleware((to) => {
  if (to.path === '/login' || to.path === '/signup') return

  const role = useAppRole()
  const layout = role === 'admin' ? 'admin' : 'user'

  setPageLayout(layout)

  if (role !== 'admin' || to.path === '/login') return

  const auth = useAuthStore()
  if (!auth.isAuthenticated || !auth.isAdmin) {
    return navigateTo(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }
})