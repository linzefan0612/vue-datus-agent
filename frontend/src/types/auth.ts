export type PermissionInfo = {
  resource: string;
  action: string;
};

export type UserInfo = {
  id: string;
  username: string;
  email: string | null;
  display_name: string | null;
  avatar_url: string | null;
  roles: string[];
  permissions: PermissionInfo[];
  is_active: boolean;
};
