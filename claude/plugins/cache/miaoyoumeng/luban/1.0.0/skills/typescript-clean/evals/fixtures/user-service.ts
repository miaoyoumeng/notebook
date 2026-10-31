interface User {
  id: string;
  name: string;
  email: string;
  active: boolean;
}

const d = new Map<string, User>();
const list = new Map<string, User>();

const sendEmail = (to: string, body: string): void => {
  console.log(`send email to ${to}: ${body}`);
};

const process = (user: User): boolean => {
  if (user) {
    if (user.email) {
      if (user.email.includes('@')) {
        if (user.name && user.name.length >= 2) {
          const existing = d.get(user.email);
          if (!existing) {
            user.email = user.email.trim().toLowerCase();
            d.set(user.email, user);
            list.set(user.id, user);
            sendEmail(user.email, `Welcome ${user.name}`);
            return true;
          } else {
            throw new Error('duplicate email');
          }
        } else {
          throw new Error('invalid name');
        }
      } else {
        throw new Error('invalid email');
      }
    } else {
      throw new Error('email required');
    }
  }
  return false;
};

const update = (user: User): boolean => {
  if (!user.email || !user.email.includes('@')) {
    throw new Error('invalid email');
  }
  const normalizedEmail = user.email.trim().toLowerCase();
  d.set(normalizedEmail, { ...user, email: normalizedEmail });
  return true;
};
