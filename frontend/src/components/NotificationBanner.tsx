import React from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, X } from 'lucide-react';

export interface NotificationState {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
}

interface NotificationBannerProps {
  notification: NotificationState | null;
  onClose: () => void;
}

export const NotificationBanner: React.FC<NotificationBannerProps> = ({
  notification,
  onClose,
}) => {
  if (!notification) return null;

  const bgClasses = {
    success: 'bg-emerald-950/90 border-emerald-800 text-emerald-200',
    error: 'bg-rose-950/90 border-rose-800 text-rose-200',
    warning: 'bg-amber-950/90 border-amber-800 text-amber-200',
    info: 'bg-indigo-950/90 border-indigo-800 text-indigo-200',
  }[notification.type];

  const Icon = {
    success: CheckCircle2,
    error: AlertCircle,
    warning: AlertTriangle,
    info: AlertCircle,
  }[notification.type];

  return (
    <div
      className={`mx-6 mt-3 p-3.5 rounded-xl border backdrop-blur flex items-center justify-between gap-3 shadow-lg animate-in fade-in slide-in-from-top-2 duration-200 ${bgClasses}`}
    >
      <div className="flex items-center gap-2.5">
        <Icon className="w-5 h-5 shrink-0" />
        <p className="text-sm font-medium">{notification.message}</p>
      </div>
      <button
        onClick={onClose}
        className="p-1 rounded-lg hover:bg-white/10 text-current opacity-70 hover:opacity-100 transition-opacity"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
