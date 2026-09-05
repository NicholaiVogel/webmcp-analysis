/** Shared formatting helpers (display only — no scoring logic). */

export const FORMAT = {
  TOTAL: '2,500',
  RANKED: '2,500',
  S2: '716',
  RESCORED: '1,353',
  VERIFIED: '217',
} as const;

export function score(v: number | null | undefined): string {
  return v == null ? '—' : Number.isInteger(v) ? String(v) : v.toFixed(1);
}

export function pct(v: number | null | undefined): string {
  return v == null ? '—' : `${Math.round(v * 100)}%`;
}

export function trunc(s: string | null | undefined, n: number): string {
  if (!s) return '';
  return s.length > n ? s.slice(0, n - 1).trimEnd() + '…' : s;
}

export const CRITERION_SHORT: Record<string, string> = {
  leverage: 'Leverage',
  execution: 'Execution',
  impact: 'Impact',
  creativity: 'Creativity',
};

export function verificationLabel(v: string | null | undefined): string {
  switch (v) {
    case 'VERIFIED_RUNTIME': return 'runtime verified';
    case 'VIDEO_VERIFIED': return 'video verified';
    case 'REPO_VERIFIED': return 'repo verified';
    case 'CLAIM_ONLY': return 'claims only';
    case 'FAILED': return 'failed at check';
    case 'UNVERIFIED': return 'not verified';
    default: return 'not verified';
  }
}

export function originLabel(o: string | null | undefined): string {
  switch (o) {
    case 'new': return 'built for the challenge';
    case 'pre_existing': return 'pre-existing project';
    case 'unclear': return 'origin unclear';
    default: return '';
  }
}

export function accessLabel(a: string | null | undefined): string {
  switch (a) {
    case 'none': return 'no auth';
    case 'login': return 'login required';
    case 'api-key': return 'API key required';
    default: return '';
  }
}
