/**
 * Script: check_drift.js
 * Purpose: Detect Schema Drift based on git status.
 */
const { execSync } = require('child_process');

try {
  console.log("🔍 [Arch] Verifying Contract-Schema Synchronization...");

  // 1. Get modified files from git
  const gitOutput = execSync('git status --porcelain').toString();
  const modifiedFiles = gitOutput.split('\n').filter(Boolean);

  if (modifiedFiles.length === 0) {
    console.log("✅ No modified files. Clean state.");
    process.exit(0);
  }

  // 2. Define detection logic
  // Looking for Zod schema changes
  const hasSchemaChange = modifiedFiles.some(f => 
    f.includes('pbos-shared-schemas') || f.includes('src/zod')
  );
  // Looking for OpenAPI contract changes
  const hasContractChange = modifiedFiles.some(f => 
    f.includes('pbos-api-contracts') || f.includes('openapi')
  );

  // 3. Enforce Rules
  if (hasSchemaChange && !hasContractChange) {
    console.error("\n❌ [CRITICAL VIOLATION] Schema Drift Detected!");
    console.error("   Reason: 'pbos-shared-schemas' was modified, but 'pbos-api-contracts' was NOT.");
    console.error("   Rule: You cannot change the implementation/types without updating the Contract first.");
    console.error("   Action: Please update 'openapi/v1.yaml' immediately.\n");
    process.exit(1);
  }

  console.log("✅ [Pass] Contract sync check passed.");
  process.exit(0);

} catch (err) {
  console.error("❌ Git check failed. Are you in the repo root?");
  process.exit(1);
}
