const fs = require('fs');
const path = require('path');

const Ajv = require('ajv');
const YAML = require('yaml');

const repoRoot = path.resolve(__dirname, '..', '..');
const schemaPath = path.join(repoRoot, 'data.schema.yml');
const dataDir = path.join(repoRoot, 'data');

function loadYaml(filePath) {
  return YAML.parse(fs.readFileSync(filePath, 'utf8'));
}

function formatError(error) {
  const instancePath = error.instancePath || '/';
  if (error.keyword === 'enum' && Array.isArray(error.params.allowedValues)) {
    return `${instancePath} must be one of: ${error.params.allowedValues.join(', ')}`;
  }

  const message = error.message || 'validation error';
  return `${instancePath} ${message}`;
}

const ajv = new Ajv({
  allErrors: true,
  strict: false,
  validateFormats: false,
});

let validate;

try {
  const schema = loadYaml(schemaPath);
  validate = ajv.compile(schema);
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Schema compilation failed: ${message}`);
  process.exit(1);
}

const files = fs
  .readdirSync(dataDir)
  .filter((file) => /\.(ya?ml)$/i.test(file))
  .sort();

let hasErrors = false;

files.forEach((file) => {
  const filePath = path.join(dataDir, file);

  let data;
  try {
    data = loadYaml(filePath);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`${file}: YAML parse error: ${message}`);
    hasErrors = true;
    return;
  }

  const valid = validate(data);
  if (valid) {
    return;
  }

  hasErrors = true;
  console.error(`${file}:`);
  (validate.errors || []).forEach((error) => {
    console.error(`  - ${formatError(error)}`);
  });
});

if (hasErrors) {
  process.exit(1);
}
