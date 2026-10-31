interface User {
  id: string;
  email: string;
}

const users: User[] = [];

const findUser = (id: string): User | null => {
  const user = users.find((item) => item.id === id);
  return user ?? null;
};

const findUserByEmail = (email: string): User | 'NOT_FOUND' => {
  const user = users.find((item) => item.email === email);
  if (!user) return 'NOT_FOUND';
  return user;
};

const getDisplayName = (id: string): string => {
  const user = findUser(id);
  if (!user) return 'Unknown';
  return user.email;
};
