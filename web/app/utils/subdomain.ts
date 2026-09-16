export type AppPortal = 'user' | 'admin' | 'delivery'
export type AppLayoutName = 'user' | 'admin' | 'delivery'

export interface PortalConfig {
  appDomain: string
  adminSubdomain: string
  deliverySubdomain: string
}

const PORTAL_TO_LAYOUT: Record<AppPortal, AppLayoutName> = {
  user: 'user',
  admin: 'admin',
  delivery: 'delivery',
}

export function portalToLayout(portal: AppPortal): AppLayoutName {
  return PORTAL_TO_LAYOUT[portal]
}

/**
 * Normalize a raw host string so it can be compared safely.
 * Strips scheme, userinfo, port, path/query, trailing dots and leading "www.".
 * Examples:
 *   "HTTPS://ADMIN.LOGISTICS.SHENODEV.TECH:8443/" -> "admin.logistics.shenodev.tech"
 *   "localhost:3000"                              -> "localhost"
 *   "www.delivery.logistics.shenodev.tech"        -> "delivery.logistics.shenodev.tech"
 */
export function normalizeHost(raw: string | null | undefined): string {
  if (!raw) return ''
  let host = raw.trim().toLowerCase()
  if (!host) return ''

  const at = host.lastIndexOf('@')
  if (at !== -1) host = host.slice(at + 1)

  const scheme = host.indexOf('://')
  if (scheme !== -1) host = host.slice(scheme + 3)

  const boundary = host.search(/[/?#;]/)
  if (boundary !== -1) host = host.slice(0, boundary)

  const colon = host.lastIndexOf(':')
  if (colon !== -1 && /^\d+$/.test(host.slice(colon + 1))) {
    host = host.slice(0, colon)
  }

  return host.replace(/^www\./, '').replace(/\.+$/, '')
}

/**
 * Resolve which portal a request belongs to, based on its Host header.
 * Portals are matched exactly, then by subdomain boundary (a deeper subdomain
 * such as "driver-7.delivery.logistics.shenodev.tech" stays inside its portal).
 * Unknown/localhost/preview hosts fall back to the user portal.
 */
export function portalFromHost(raw: string | null | undefined, config: PortalConfig): AppPortal {
  const host = normalizeHost(raw)
  const userHost = normalizeHost(config.appDomain)
  const adminHost = normalizeHost(`${config.adminSubdomain}.${config.appDomain}`)
  const deliveryHost = normalizeHost(`${config.deliverySubdomain}.${config.appDomain}`)

  const matches = (candidate: string): boolean => {
    if (!candidate) return false
    return host === candidate || host.endsWith(`.${candidate}`)
  }

  if (matches(deliveryHost)) return 'delivery'
  if (matches(adminHost)) return 'admin'
  if (matches(userHost)) return 'user'

  return 'user'
}

export function useRuntimePortalConfig(): PortalConfig {
  const config = useRuntimeConfig()
  return {
    appDomain: String(config.public.appDomain ?? ''),
    adminSubdomain: String(config.public.adminSubdomain ?? 'admin'),
    deliverySubdomain: String(config.public.deliverySubdomain ?? 'delivery'),
  }
}

export function useAppRole(): AppPortal {
  const requestUrl = useRequestURL()
  return portalFromHost(requestUrl?.host, useRuntimePortalConfig())
}