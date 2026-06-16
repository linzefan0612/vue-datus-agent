<script setup lang="ts">
import { onMounted, shallowRef } from "vue";
import { Shield, UserX, UserCheck, Loader2 } from "@lucide/vue";
import Button from "@/components/ui/Button.vue";
import Badge from "@/components/ui/Badge.vue";
import { requestJson, extractResultData } from "@/lib/chat";
import { useConnection } from "@/composables/useConnection";
import type { UserInfo } from "@/types/auth";

const { effectiveBase } = useConnection();
const users = shallowRef<UserInfo[]>([]);
const loading = shallowRef(true);

onMounted(async () => {
  await loadUsers();
});

async function loadUsers() {
  loading.value = true;
  try {
    const data = await requestJson<{ success: boolean; data: { users: UserInfo[]; total: number } }>(
      effectiveBase(),
      "/api/v1/fund/users"
    ).then(extractResultData<{ users: UserInfo[]; total: number }>);
    users.value = data?.users ?? [];
  } catch {
    users.value = [];
  } finally {
    loading.value = false;
  }
}

async function toggleActive(user: UserInfo) {
  const endpoint = user.is_active ? "deactivate" : "activate";
  await requestJson(effectiveBase(), `/api/v1/fund/users/${user.id}/${endpoint}`, { method: "POST" });
  await loadUsers();
}

async function assignAdmin(user: UserInfo) {
  await requestJson(effectiveBase(), `/api/v1/fund/users/${user.id}/roles`, {
    method: "POST",
    body: JSON.stringify({ role_id: "admin" }),
  });
  await loadUsers();
}

async function revokeAdmin(user: UserInfo) {
  await requestJson(effectiveBase(), `/api/v1/fund/users/${user.id}/roles/admin`, { method: "DELETE" });
  await loadUsers();
}
</script>

<template>
  <div class="userManager">
    <div class="userManagerHeader">
      <Shield :size="20" />
      <h2>User Management</h2>
    </div>

    <div v-if="loading" class="userManagerLoading">
      <Loader2 class="spin" :size="20" />
    </div>

    <table v-else class="userTable">
      <thead>
        <tr>
          <th>User</th>
          <th>Email</th>
          <th>Roles</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>
            <div class="userCell">
              <img v-if="u.avatar_url" :src="u.avatar_url" :alt="u.username" class="userAvatar" />
              <div class="userAvatarPlaceholder" v-else>{{ (u.display_name || u.username).charAt(0).toUpperCase() }}</div>
              <span>{{ u.display_name || u.username }}</span>
            </div>
          </td>
          <td>{{ u.email || "-" }}</td>
          <td>
            <Badge v-for="role in u.roles" :key="role" :variant="role === 'admin' ? 'default' : 'secondary'">
              {{ role }}
            </Badge>
          </td>
          <td>
            <Badge :variant="u.is_active ? 'default' : 'destructive'">
              {{ u.is_active ? "Active" : "Inactive" }}
            </Badge>
          </td>
          <td class="actionsCell">
            <Button
              v-if="!u.roles.includes('admin')"
              size="sm"
              variant="outline"
              @click="assignAdmin(u)"
            >
              <Shield :size="14" />
              Admin
            </Button>
            <Button
              v-else
              size="sm"
              variant="outline"
              @click="revokeAdmin(u)"
            >
              Revoke Admin
            </Button>
            <Button
              size="sm"
              :variant="u.is_active ? 'outline' : 'default'"
              @click="toggleActive(u)"
            >
              <UserX v-if="u.is_active" :size="14" />
              <UserCheck v-else :size="14" />
              {{ u.is_active ? "Deactivate" : "Activate" }}
            </Button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.userManager {
  padding: 24px;
  max-width: 960px;
}

.userManagerHeader {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.userManagerHeader h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.userManagerLoading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.userTable {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.userTable th {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-weight: 500;
}

.userTable td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}

.userCell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.userAvatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.userAvatarPlaceholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
}

.actionsCell {
  display: flex;
  gap: 6px;
}
</style>
