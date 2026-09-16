export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (auth.status === 'idle') {
    await auth.hydrate()
  }

  if (!auth.isAuthenticated) {
    const refreshed = await auth.tryRefresh()
    if (refreshed) {
      await auth.hydrate()
    }
  }

  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: redirectQuery(to.fullPath) })
  }
})