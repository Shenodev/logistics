import { SESSION_COOKIE, type LoginResponse, type SessionUser } from '../../../shared/auth'
import { findDevUser } from '../../utils/devRegistry'

interface Account {
  email: string
  password: string
  name: string
  role: SessionUser['role']
}

function resolveAccount(config: Record<string, unknown>, email: string, password: string): Account | null {
  const seeded: Account[] = [
    {
      email: String(config.devAdminEmail),
      password: String(config.devAdminPassword),
      name: 'Sheno Admin',
      role: 'admin',
    },
    {
      email: String(config.devUserEmail),
      password: String(config.devUserPassword),
      name: 'Sheno User',
      role: 'user',
    },
  ]

  const match = seeded.find((account) => account.email === email && account.password === password)
  if (match) return match

  const registered = findDevUser(email)
  if (registered && registered.password === password) {
    return { email: registered.email, password: registered.password, name: registered.name, role: registered.role }
  }

  return null
}

export default defineEventHandler(async (event): Promise<LoginResponse> => {
  const config = useRuntimeConfig(event).auth
  const body = await readBody<{ email?: string; password?: string }>(event).catch(() => ({}))

  const email = String(body?.email ?? '').trim().toLowerCase()
  const password = String(body?.password ?? '')

  if (!email || !password) {
    throw createError({ statusCode: 400, statusMessage: 'Email and password are required' })
  }

  const account = resolveAccount(config, email, password)
  if (!account) {
    throw createError({ statusCode: 401, statusMessage: 'Invalid credentials' })
  }

  const user: SessionUser = {
    id: `dev-${account.role}`,
    email: account.email,
    name: account.name,
    role: account.role,
  }

  const token = signSession(event, {
    sub: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
  })

  setCookie(event, SESSION_COOKIE, token, sessionCookieOptions(event))

  return { user }
})