/**
 * IMPLEMENTS: S120-S126
 * Type definitions for Phantom Guard VS Code Extension
 */

export type RiskLevel = 'SAFE' | 'SUSPICIOUS' | 'HIGH_RISK' | 'NOT_FOUND' | 'ERROR';

export interface PackageRisk {
  name: string;
  risk_level: RiskLevel;
  risk_score: number;
  signals: string[];
  recommendation?: string;
}

export interface ValidationResult {
  packages: PackageRisk[];
  total: number;
  safe: number;
  suspicious: number;
  highRisk: number;
  notFound: number;
}
