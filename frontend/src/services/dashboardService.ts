import { MOCK_DASHBOARD_DATA } from '../data/mockDashboard';
import type { DashboardData } from '../types/dashboard';

/**
 * Mock dashboard data service.
 *
 * This is the ONLY module the Dashboard page talks to for account data.
 * It simulates network latency (and an occasional failure, so the
 * error/retry UI is actually reachable during the demo) and resolves the
 * shared mock dashboard data. Later, `getDashboardData()` can be
 * reimplemented to call the real backend (e.g. GET /dashboard) with an
 * identical return shape — no page/component changes required.
 */

const MOCK_DASHBOARD_DELAY_MS = 900;

/** Simulated chance of a failed load, so "Couldn't load balance" + Retry is demoable. */
const MOCK_FAILURE_RATE = 0.15;

export const mockDashboardService = {
  getDashboardData(): Promise<DashboardData> {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() < MOCK_FAILURE_RATE) {
          reject(new Error("Couldn't load balance"));
          return;
        }
        resolve(MOCK_DASHBOARD_DATA);
      }, MOCK_DASHBOARD_DELAY_MS);
    });
  },
};
