export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuthStore()

  if (auth.status === 'idle') {
    await auth.hydrate()
  }

  if (auth.isAuthenticated) {
    return navigateTo('/')
  }
})