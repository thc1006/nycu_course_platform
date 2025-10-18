/**
 * K6 Baseline Load Test
 *
 * Purpose: Establish performance baseline for NYCU Course Platform
 * Duration: 5 minutes
 * Virtual Users: 20 concurrent users
 * Target: Measure API and system performance under normal load
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp-up to 10 users
    { duration: '1m', target: 20 },   // Ramp-up to 20 users
    { duration: '3m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp-down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95% of requests must complete within 500ms
    'http_req_failed': ['rate<0.05'],     // Error rate must be below 5%
    'errors': ['rate<0.05'],              // Custom error rate
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // Test 1: Health Check
  let response = http.get(`${BASE_URL}/health`);
  let checkRes = check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check is healthy': (r) => r.json('status') === 'healthy',
  });
  errorRate.add(!checkRes);

  sleep(1);

  // Test 2: Get Semesters
  response = http.get(`${BASE_URL}/api/semesters`);
  checkRes = check(response, {
    'semesters status is 200': (r) => r.status === 200,
    'semesters response time < 200ms': (r) => r.timings.duration < 200,
  });
  errorRate.add(!checkRes);

  sleep(1);

  // Test 3: Get Courses (with pagination)
  response = http.get(`${BASE_URL}/api/courses?limit=50&offset=0`);
  checkRes = check(response, {
    'courses status is 200': (r) => r.status === 200,
    'courses response time < 300ms': (r) => r.timings.duration < 300,
    'courses returns data': (r) => r.json().length > 0,
  });
  errorRate.add(!checkRes);

  sleep(2);

  // Test 4: Search Courses
  const searchTerms = ['資料結構', '微積分', '程式設計', 'English', '通識'];
  const randomTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  response = http.get(`${BASE_URL}/api/courses?q=${encodeURIComponent(randomTerm)}&limit=20`);
  checkRes = check(response, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 400ms': (r) => r.timings.duration < 400,
  });
  errorRate.add(!checkRes);

  sleep(1);

  // Test 5: Get Specific Course
  const courseId = Math.floor(Math.random() * 1000) + 1;
  response = http.get(`${BASE_URL}/api/courses/${courseId}`);
  checkRes = check(response, {
    'get course response time < 200ms': (r) => r.timings.duration < 200,
  });
  // Don't count 404 as error since random ID might not exist
  if (response.status !== 404) {
    errorRate.add(!checkRes);
  }

  sleep(2);
}

export function handleSummary(data) {
  return {
    'tests/results/baseline-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = (options && options.indent) || '';
  const colors = (options && options.enableColors) !== undefined ? options.enableColors : false;

  const metrics = data.metrics;

  let output = `\n${indent}📊 NYCU Course Platform - Baseline Load Test Results\n`;
  output += `${indent}${'='.repeat(60)}\n\n`;

  output += `${indent}📈 Test Summary:\n`;
  output += `${indent}  Duration: 5 minutes\n`;
  output += `${indent}  Virtual Users: 0 → 10 → 20 → 0\n`;
  output += `${indent}  Total Requests: ${metrics.http_reqs?.values?.count || 0}\n`;
  output += `${indent}  Request Rate: ${(metrics.http_reqs?.values?.rate || 0).toFixed(2)}/s\n\n`;

  output += `${indent}⚡ Performance Metrics:\n`;
  output += `${indent}  HTTP Request Duration:\n`;
  output += `${indent}    • Min: ${(metrics.http_req_duration?.values?.min || 0).toFixed(2)}ms\n`;
  output += `${indent}    • Med: ${(metrics.http_req_duration?.values?.med || 0).toFixed(2)}ms\n`;
  output += `${indent}    • P90: ${(metrics.http_req_duration?.values['p(90)'] || 0).toFixed(2)}ms\n`;
  output += `${indent}    • P95: ${(metrics.http_req_duration?.values['p(95)'] || 0).toFixed(2)}ms\n`;
  output += `${indent}    • Max: ${(metrics.http_req_duration?.values?.max || 0).toFixed(2)}ms\n\n`;

  output += `${indent}✅ Success Rate:\n`;
  const successRate = (1 - (metrics.http_req_failed?.values?.rate || 0)) * 100;
  output += `${indent}  • Success: ${successRate.toFixed(2)}%\n`;
  output += `${indent}  • Failed: ${((metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%\n`;
  output += `${indent}  • Error Rate: ${((metrics.errors?.values?.rate || 0) * 100).toFixed(2)}%\n\n`;

  output += `${indent}🎯 Threshold Status:\n`;
  const thresholds = data.root_group?.checks || [];
  for (const [name, value] of Object.entries(metrics)) {
    if (value.thresholds) {
      for (const [thresholdName, result] of Object.entries(value.thresholds)) {
        const status = result.ok ? '✅ PASS' : '❌ FAIL';
        output += `${indent}  ${status}: ${name} - ${thresholdName}\n`;
      }
    }
  }

  output += `\n${indent}${'='.repeat(60)}\n`;

  return output;
}
