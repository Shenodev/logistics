import { createHmac, timingSafeEqual } from 'node:crypto'
import { SESSION_COOKIE_OPTIONS, type SessionJwtPayload } from '../../shared/auth'

function b64url(input: string | Buffer): string {
  return Buffer.from(input).toString('base64url')
}

export function sessionCookieOptions(event: H3Event) {
  const secure = useRuntimeConfig(event).auth.cookieSecure
  return { ...SESSION_COOKIE_OPTIONS, secure: Boolean(secure) }
}

export function signSession(event: H3Event, payload: Omit<SessionJwtPayload, 'iat' | 'exp'>): string {
  const config = useRuntimeConfig(event)
  const ttl = Number(config.auth.sessionTtlSeconds)
  const iat = Math.floor(Date.now() / 1000)
  const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const body = b64url(JSON.stringify({ ...payload, iat, exp: iat + ttl }))
  const signature = b64url(createHmac('sha256', config.auth.sessionSecret).update(`${header}.${body}`).digest())
  return `${header}.${body}.${signature}`
}

export function verifySession(event: H3Event, token: string): SessionJwtPayload | null {
  const parts = token.split('.')
  if (parts.length !== 3) return null

  const config = useRuntimeConfig(event)
  const expected = b64url(createHmac('sha256', config.auth.sessionSecret).update(`${parts[0]}.${parts[1]}`).digest())
  const actual = Buffer.from(parts[2])
  const expectedBuffer = Buffer.from(expected)

  if (actual.length !== expectedBuffer.length || !timingSafeEqual(actual, expectedBuffer)) return null

  try {
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString()) as SessionJwtPayload
    if (typeof payload.exp !== 'number' || payload.exp < Math.floor(Date.now() / 1000)) return null
    return payload
  }
  catch {
    return null
  }
}