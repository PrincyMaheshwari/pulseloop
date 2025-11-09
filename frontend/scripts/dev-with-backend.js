const { spawn } = require('child_process');
const net = require('net');
const path = require('path');

const BACKEND_PORT = Number(process.env.BACKEND_PORT || 8000);
const BACKEND_HOST = process.env.BACKEND_HOST || '127.0.0.1';
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const NEXT_PORT = process.env.PORT || 3000;

function waitForPort({ host, port, timeout = 15000 }) {
  const start = Date.now();

  return new Promise((resolve, reject) => {
    const check = () => {
      const socket = new net.Socket();
      socket
        .once('error', err => {
          socket.destroy();
          if (Date.now() - start >= timeout) {
            reject(new Error(`Timed out waiting for ${host}:${port} (${err.message})`));
          } else {
            setTimeout(check, 500);
          }
        })
        .once('connect', () => {
          socket.end();
          resolve(true);
        })
        .connect(port, host);
    };

    check();
  });
}

async function ensureBackend() {
  try {
    await waitForPort({ host: BACKEND_HOST, port: BACKEND_PORT, timeout: 2000 });
    console.log(`[dev] Backend already running at ${BACKEND_URL}`);
    return null;
  } catch {
    console.log('[dev] Backend not detected, starting FastAPI with uvicorn…');
  }

  const backendProcess = spawn('uvicorn', ['app.main:app', '--reload', '--port', String(BACKEND_PORT)], {
    cwd: path.resolve(__dirname, '../../backend'),
    stdio: 'inherit',
    shell: true,
  });

  backendProcess.on('exit', code => {
    if (code !== null) {
      console.log(`[dev] Backend process exited with code ${code}`);
    }
  });

  await waitForPort({ host: BACKEND_HOST, port: BACKEND_PORT, timeout: 20000 });
  console.log(`[dev] Backend ready at ${BACKEND_URL}`);

  return backendProcess;
}

async function start() {
  let backendProcess = null;
  try {
    backendProcess = await ensureBackend();
  } catch (error) {
    console.error('[dev] Failed to start backend:', error.message);
    process.exit(1);
  }

  const env = {
    ...process.env,
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || BACKEND_URL,
  };

  console.log(`[dev] Launching Next.js dev server on http://localhost:${NEXT_PORT}`);

  const frontendProcess = spawn('npm', ['run', 'dev'], {
    cwd: path.resolve(__dirname, '..'),
    stdio: 'inherit',
    shell: true,
    env,
  });

  const cleanup = () => {
    if (frontendProcess && !frontendProcess.killed) {
      frontendProcess.kill('SIGINT');
    }
    if (backendProcess && !backendProcess.killed) {
      backendProcess.kill('SIGINT');
    }
  };

  frontendProcess.on('exit', code => {
    if (code !== null) {
      console.log(`[dev] Frontend exited with code ${code}`);
    }
    cleanup();
  });

  process.on('SIGINT', () => {
    cleanup();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    cleanup();
    process.exit(0);
  });
}

start();

