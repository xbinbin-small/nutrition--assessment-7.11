#!/usr/bin/env node

/**
 * 检测可用的Python命令
 * 优先级: python3 > python
 */

const { execSync } = require('child_process');

function checkCommand(cmd) {
  try {
    execSync(`${cmd} --version`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

if (checkCommand('python3')) {
  console.log('python3');
} else if (checkCommand('python')) {
  console.log('python');
} else {
  console.error('Error: Python is not installed');
  process.exit(1);
}
