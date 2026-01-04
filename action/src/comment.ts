/**
 * IMPLEMENTS: S104
 * INVARIANTS: INV105, INV106
 * TESTS: T104.01-T104.05
 *
 * PR comment generation for Phantom Guard GitHub Action.
 *
 * Generates and updates sticky PR comments with validation results.
 */

import * as core from '@actions/core';
import * as github from '@actions/github';
import { ValidationResult } from './validate';
import { ValidationSummary } from './exit';

/**
 * Comment identifier for finding and updating existing comments.
 */
const COMMENT_IDENTIFIER = '<!-- phantom-guard-action -->';

/**
 * IMPLEMENTS: S104
 * INVARIANT: INV105 - Comments are updated, not duplicated (sticky mode)
 * INVARIANT: INV106 - Comment body never exceeds GitHub limits
 *
 * Generate or update a PR comment with validation results.
 *
 * @param results - Validation results for all packages
 * @param summary - Summary of validation results
 * @param token - GitHub token for API access
 */
export async function generatePRComment(
  results: ValidationResult[],
  summary: ValidationSummary,
  token: string
): Promise<void> {
  const context = github.context;

  // Only run on pull requests
  if (!context.payload.pull_request) {
    core.info('Not a pull request, skipping PR comment');
    return;
  }

  if (!token) {
    core.warning('No GitHub token provided, skipping PR comment');
    return;
  }

  const octokit = github.getOctokit(token);
  const prNumber = context.payload.pull_request.number;
  const owner = context.repo.owner;
  const repo = context.repo.repo;

  // Generate comment body
  const body = generateCommentBody(results, summary);

  // INV106: Ensure comment body doesn't exceed GitHub's limit (65536 characters)
  const maxLength = 65536;
  const truncatedBody =
    body.length > maxLength
      ? body.substring(0, maxLength - 100) + '\n\n... (truncated due to length)'
      : body;

  try {
    // INV105: Find existing comment to update (sticky mode)
    const existingComment = await findExistingComment(octokit, owner, repo, prNumber);

    if (existingComment) {
      // Update existing comment
      await octokit.rest.issues.updateComment({
        owner,
        repo,
        comment_id: existingComment.id,
        body: truncatedBody,
      });
      core.info(`Updated existing PR comment #${existingComment.id}`);
    } else {
      // Create new comment
      const response = await octokit.rest.issues.createComment({
        owner,
        repo,
        issue_number: prNumber,
        body: truncatedBody,
      });
      core.info(`Created new PR comment #${response.data.id}`);
    }
  } catch (error) {
    core.warning(
      `Failed to post PR comment: ${error instanceof Error ? error.message : error}`
    );
  }
}

/**
 * Find existing Phantom Guard comment on the PR.
 */
async function findExistingComment(
  octokit: ReturnType<typeof github.getOctokit>,
  owner: string,
  repo: string,
  prNumber: number
): Promise<{ id: number } | undefined> {
  const comments = await octokit.rest.issues.listComments({
    owner,
    repo,
    issue_number: prNumber,
    per_page: 100,
  });

  for (const comment of comments.data) {
    if (comment.body?.includes(COMMENT_IDENTIFIER)) {
      return { id: comment.id };
    }
  }

  return undefined;
}

/**
 * Generate the comment body markdown.
 */
function generateCommentBody(
  results: ValidationResult[],
  summary: ValidationSummary
): string {
  const lines: string[] = [COMMENT_IDENTIFIER, ''];

  // Header
  lines.push('# Phantom Guard Security Report');
  lines.push('');

  // Summary badge
  if (summary.highRiskCount > 0) {
    lines.push('**Status:** :x: High-risk packages detected');
  } else if (summary.suspiciousCount > 0) {
    lines.push('**Status:** :warning: Suspicious packages detected');
  } else {
    lines.push('**Status:** :white_check_mark: All packages validated as safe');
  }

  lines.push('');

  // Summary table
  lines.push('## Summary');
  lines.push('');
  lines.push('| Metric | Count |');
  lines.push('|:-------|------:|');
  lines.push(`| Total packages | ${summary.totalPackages} |`);
  lines.push(`| Safe | ${summary.safeCount} |`);
  lines.push(`| Suspicious | ${summary.suspiciousCount} |`);
  lines.push(`| High-risk | ${summary.highRiskCount} |`);
  lines.push('');

  // High-risk packages
  const highRisk = results.filter((r) => r.riskLevel === 'high-risk');
  if (highRisk.length > 0) {
    lines.push('## :x: High-Risk Packages');
    lines.push('');
    lines.push('These packages may be AI-hallucinated or malicious:');
    lines.push('');
    lines.push('| Package | Score | Signals | File |');
    lines.push('|:--------|------:|:--------|:-----|');
    for (const pkg of highRisk) {
      const fileRef = pkg.lineNumber
        ? `${pkg.sourceFile}:${pkg.lineNumber}`
        : pkg.sourceFile;
      lines.push(
        `| \`${pkg.package}\` | ${(pkg.riskScore * 100).toFixed(0)}% | ${pkg.signals.join(', ')} | ${fileRef} |`
      );
    }
    lines.push('');
  }

  // Suspicious packages
  const suspicious = results.filter((r) => r.riskLevel === 'suspicious');
  if (suspicious.length > 0) {
    lines.push('## :warning: Suspicious Packages');
    lines.push('');
    lines.push('These packages warrant additional review:');
    lines.push('');
    lines.push('| Package | Score | Signals | File |');
    lines.push('|:--------|------:|:--------|:-----|');
    for (const pkg of suspicious.slice(0, 20)) {
      // Limit to 20
      const fileRef = pkg.lineNumber
        ? `${pkg.sourceFile}:${pkg.lineNumber}`
        : pkg.sourceFile;
      lines.push(
        `| \`${pkg.package}\` | ${(pkg.riskScore * 100).toFixed(0)}% | ${pkg.signals.join(', ')} | ${fileRef} |`
      );
    }
    if (suspicious.length > 20) {
      lines.push(`| ... | ... | ... | ${suspicious.length - 20} more |`);
    }
    lines.push('');
  }

  // Recommendations
  if (highRisk.length > 0 || suspicious.length > 0) {
    lines.push('## Recommendations');
    lines.push('');
    lines.push('1. **Verify package existence** on the official registry');
    lines.push('2. **Check package ownership** and maintenance history');
    lines.push('3. **Review package code** before installation');
    lines.push('4. **Consider alternatives** from well-known publishers');
    lines.push('');
  }

  // Footer
  lines.push('---');
  lines.push(
    '*Powered by [Phantom Guard](https://github.com/phantom-guard/phantom-guard) - Detecting AI-hallucinated package attacks*'
  );

  return lines.join('\n');
}
