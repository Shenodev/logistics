export function isSafeRedirect(target: string): boolean {
  if (!target) return false
  if (!target.startsWith('/')) return false
  if (target.startsWith('//')) return false
  if (target.startsWith('/\\')) return false
  return true
}

export function redirectQuery(fullPath: string): Record<string, string> {
  return isSafeRedirect(fullPath) ? { redirect: fullPath } : {}
}

export function safeRedirectTarget(value: unknown, fallback = '/'): string {
  return typeof value === 'string' && isSafeRedirect(value) ? value : fallback
}