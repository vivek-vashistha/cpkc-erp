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

export function getRPAStatusColor(status: string): string {
  switch (status) {
    case 'Auto Fix':
      return 'bg-green-100 text-green-800';
    case 'Manual Review Required':
      return 'bg-orange-100 text-orange-800';
    case 'Needs Data':
      return 'bg-yellow-100 text-yellow-800';
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800';
    case 'SUBMITTED':
      return 'bg-blue-100 text-blue-800';
    case 'IN_PROGRESS':
      return 'bg-indigo-100 text-indigo-800';
    case 'COMPLETED':
      return 'bg-green-100 text-green-800';
    case 'FAILED':
      return 'bg-red-100 text-red-800';
    case 'CANCELLED':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

export function getRPAStatusIcon(status: string): string {
  switch (status) {
    case 'Auto Fix':
      return '🤖';
    case 'Manual Review Required':
      return '👤';
    case 'Needs Data':
      return '📋';
    case 'PENDING':
      return '⏳';
    case 'SUBMITTED':
      return '📤';
    case 'IN_PROGRESS':
      return '⚙️';
    case 'COMPLETED':
      return '✅';
    case 'FAILED':
      return '❌';
    case 'CANCELLED':
      return '🚫';
    default:
      return '❓';
  }
}

export function formatRPAProgress(completed: number, total: number): string {
  if (total === 0) return '0%';
  const percentage = Math.round((completed / total) * 100);
  return `${percentage}%`;
}

export function isRPAEligible(anomaly: any): boolean {
  return anomaly.suggested_fix && 
         anomaly.suggested_fix !== 'Manual review required' &&
         anomaly.confidence > 0.7 &&
         (!anomaly.rpa_status || anomaly.rpa_status === 'Auto Fix');
}

export function getRPAEligibilityReason(anomaly: any): string {
  if (!anomaly.suggested_fix || anomaly.suggested_fix === 'Manual review required') {
    return 'No automated fix available';
  }
  if (anomaly.confidence <= 0.7) {
    return 'Confidence too low for auto-fix';
  }
  if (anomaly.rpa_status === 'Manual Review Required') {
    return 'Requires manual review';
  }
  if (anomaly.rpa_status === 'Needs Data') {
    return 'Needs additional data';
  }
  if (anomaly.rpa_status && anomaly.rpa_status !== 'Auto Fix') {
    return 'Already processed';
  }
  return 'Eligible for RPA';
}
