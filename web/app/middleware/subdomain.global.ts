export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/login' || to.path === '/signup') return

  const role = useAppRole()
  setPageLayout(portalToLayout(role))

  if (role !== 'admin' || to.path === '/login') return

  const auth = useAuthStore()

  if (auth.status === 'idle') {
    await auth.hydrate()
  }

  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/login', query: redirectQuery(to.fullPath) })
  }

  if (!auth.isAdmin) {
    const appDomain = String(useRuntimeConfig().public.appDomain)
    const hostname = useRequestURL().hostname
    if (hostname !== appDomain) {
      return navigateTo(`https://${appDomain}/`, { external: true })
    }
    return navigateTo('/')
  }
})