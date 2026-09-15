export default defineNuxtRouteMiddleware(() => {
  const role = useAppRole()
  const layout = role === 'admin' ? 'admin' : 'user'

  setPageLayout(layout)
})