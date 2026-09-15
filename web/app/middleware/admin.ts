export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (auth.status === 'idle') {
    await auth.hydrate()
  }

  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: redirectQuery(to.fullPath) })
  }

  if (!auth.isAdmin) {
    return navigateTo('/')
  }
})