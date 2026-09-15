export type AppRole = 'user' | 'admin' | 'unknown'

export function useAppRole(): AppRole {
  const config = useRuntimeConfig()
  const hostname = useRequestURL().hostname
  const appDomain = config.public.appDomain as string
  const adminSubdomain = config.public.adminSubdomain as string
  const adminHost = `${adminSubdomain}.${appDomain}`

  if (hostname === adminHost || hostname.endsWith(`.${adminHost}`)) {
    return 'admin'
  }

  if (hostname === appDomain || hostname.endsWith(`.${appDomain}`)) {
    return 'user'
  }

  return 'unknown'
}