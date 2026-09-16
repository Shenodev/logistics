export default defineNuxtRouteMiddleware(() => {
  if (useAppRole() !== 'delivery') {
    return navigateTo({ path: '/login' })
  }
})