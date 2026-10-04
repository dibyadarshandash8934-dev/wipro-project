/** Status badge component. */

interface StatusBadgeProps {
  status: string;
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
}

const variantStyles: Record<string, string> = {
  success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  error: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
};

const statusVariants: Record<string, string> = {
  ACTIVE: 'success',
  CONNECTED: 'success',
  DISCONNECTED: 'error',
  CHECKING: 'warning',
  EXPIRED: 'warning',
};

export default function StatusBadge({ status, variant = 'default' }: StatusBadgeProps) {
  const variantClass = variantStyles[statusVariants[status] ?? variant];
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClass}`}
    >
      {status}
    </span>
  );
}