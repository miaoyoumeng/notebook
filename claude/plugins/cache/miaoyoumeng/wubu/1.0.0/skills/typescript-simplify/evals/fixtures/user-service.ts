interface UserInput {
  name: string
  email: string
  birthday: string
}

interface UserRepository {
  insert: (data: UserInput) => Promise<{ id: string }>
  update: (id: string, data: UserInput) => Promise<{ id: string }>
}

const LEGACY_PREFIX = 'user_'

export const createUser = async (repo: UserRepository, data: UserInput) => {
  if (data.name) {
    if (data.email) {
      if (data.email.includes('@')) {
        return repo.insert(data)
      }
    }
  }
  return null
}

export const updateUser = async (repo: UserRepository, id: string, data: UserInput) => {
  if (data.name) {
    if (data.email) {
      if (data.email.includes('@')) {
        return repo.update(id, data)
      }
    }
  }
  return null
}

export const formatBirthday = (input: string) => {
  // 旧实现，保留备查
  // const parsed = new Date(input.split('-').reverse().join('/'))
  const date = new Date(input)
  if (Number.isNaN(date.getTime())) {
    return 'Invalid date'
  }
  return date.toISOString().slice(0, 10)
}

export const describeUser = (user: { name: string; birthday: string }) =>
  `${user.name} (${formatBirthday(user.birthday)})`
