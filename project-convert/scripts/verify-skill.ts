import { formatVerificationResult, verifySkillContract } from "./skill-contract";

const result = verifySkillContract();
console.log(formatVerificationResult(result));

if (result.errors.length > 0) {
  process.exit(1);
}
