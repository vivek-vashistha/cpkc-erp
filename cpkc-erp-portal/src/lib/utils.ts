import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatCurrency(amount: number, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function getStatusColor(status: string) {
  switch (status.toLowerCase()) {
    case 'new':
    case 'open':
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'resolved':
    case 'completed':
    case 'paid':
      return 'bg-blue-100 text-blue-800'
    case 'ignored':
    case 'cancelled':
    case 'overdue':
      return 'bg-red-100 text-red-800'
    case 'in transit':
    case 'partially paid':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
