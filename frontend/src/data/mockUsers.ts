import type { RecipientUser } from '../types/user';

/**
 * Single source of truth for mock "send money" recipients. Nothing
 * outside this file should hardcode a recipient's name/handle/contact
 * info — `mockUserService` reads from here, and the UI only ever talks
 * to `mockUserService`. When the real backend is wired up, this file is
 * deleted and the service starts calling a real user-directory/search
 * API instead.
 */
export const MOCK_USERS: RecipientUser[] = [
  {
    id: 'user_2001',
    name: 'Rafiq Islam',
    handle: 'rafiq.islam',
    email: 'rafiq.islam@example.com',
    phone: '+880 1712-345678',
  },
  {
    id: 'user_2002',
    name: 'Nusrat Jahan',
    handle: 'nusrat.jahan',
    email: 'nusrat.jahan@example.com',
    phone: '+880 1812-223344',
  },
  {
    id: 'user_2003',
    name: 'Karim Uddin',
    handle: 'karim.uddin',
    email: 'karim.uddin@example.com',
    phone: '+880 1911-556677',
  },
  {
    id: 'user_2004',
    name: 'Farzana Akter',
    handle: 'farzana.akter',
    email: 'farzana.akter@example.com',
    phone: '+880 1611-889900',
  },
  {
    id: 'user_2005',
    name: 'Shakil Ahmed',
    handle: 'shakil.ahmed',
    email: 'shakil.ahmed@example.com',
    phone: '+880 1512-334455',
  },
  {
    id: 'user_2006',
    name: 'Mahmuda Begum',
    handle: 'mahmuda.begum',
    email: 'mahmuda.begum@example.com',
    phone: '+880 1712-998877',
  },
  {
    id: 'user_2007',
    name: 'Tanvir Hasan',
    handle: 'tanvir.hasan',
    email: 'tanvir.hasan@example.com',
    phone: '+880 1812-667788',
  },
  {
    id: 'user_2008',
    name: 'Sabrina Yasmin',
    handle: 'sabrina.yasmin',
    email: 'sabrina.yasmin@example.com',
    phone: '+880 1911-112233',
  },
  {
    id: 'user_1001',
    name: 'Amina Rahman',
    handle: 'amina.rahman',
    email: 'amina@itcarnival.com',
    phone: '+880 1711-234567',
  },
];
