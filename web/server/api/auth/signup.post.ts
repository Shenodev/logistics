import { SESSION_COOKIE, type LoginResponse, type SessionUser } from '../../../shared/auth'
import { findDevUser, registerDevUser } from '../../utils/devRegistry'

export default defineEventHandler(async (event): Promise<LoginResponse> => {
  const config = useRuntimeConfig(event).auth
  const body = await readBody<{ name?: string; email?: string; password?: string }>(event).catch(() => ({}))

  const name = String(body?.name ?? '').trim()
  const email = String(body?.email ?? '').trim().toLowerCase()
  const password = String(body?.password ?? '')

  if (!name || !email || !password) {
    throw createError({ statusCode: 400, statusMessage: 'Name, email and password are required' })
  }
  if (password.length < 8) {
    throw createError({ statusCode: 400, statusMessage: 'Password must be at least 8 characters' })
  }

  const reserved = [String(config.devAdminEmail), String(config.devUserEmail)]
  if (reserved.includes(email) || findDevUser(email)) {
    throw createError({ statusCode: 409, statusMessage: 'An account with this email already exists' })
  }

  const user: SessionUser = {
    id: `signup-${email}`,
    email,
    name,
    role: 'user',
  }

  registerDevUser({ ...user, password })

  const token = signSession(event, {
    sub: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
  })

  setCookie(event, SESSION_COOKIE, token, sessionCookieOptions(event))

  return { user }
})