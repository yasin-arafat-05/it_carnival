import { apiFetch } from '../config/api';

export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  reference_id?: string;
  created_at: string;
}

export const notificationService = {
  async getNotifications(): Promise<NotificationItem[]> {
    return await apiFetch<NotificationItem[]>('/notifications');
  },

  async markAsRead(notificationId: string): Promise<NotificationItem> {
    return await apiFetch<NotificationItem>(`/notifications/${notificationId}/read`, {
      method: 'PATCH',
    });
  },

  async markAllAsRead(): Promise<{ message: string }> {
    return await apiFetch<{ message: string }>('/notifications/read-all', {
      method: 'PATCH',
    });
  },
};
