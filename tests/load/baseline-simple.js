/**
 * K6 Baseline Load Test - Simplified Version
 *
 * Purpose: Establish performance baseline for NYCU Course Platform
 * Duration: 5 minutes
 * Virtual Users: 20 concurrent users
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 10 },
    { duration: '1m', target: 20 },
    { duration: '3m', target: 20 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],
    'http_req_failed': ['rate<0.05'],
    'errors': ['rate<0.05'],
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // Test 1: Health Check
  let response = http.get(BASE_URL + '/health');
  let checkRes = check(response, {
    'health check status is 200': function(r) { return r.status === 200; },
    'health check is healthy': function(r) { return r.json('status') === 'healthy'; },
  });
  errorRate.add(!checkRes);
  sleep(1);

  // Test 2: Get Semesters
  response = http.get(BASE_URL + '/api/semesters');
  checkRes = check(response, {
    'semesters status is 200': function(r) { return r.status === 200; },
    'semesters response time < 200ms': function(r) { return r.timings.duration < 200; },
  });
  errorRate.add(!checkRes);
  sleep(1);

  // Test 3: Get Courses
  response = http.get(BASE_URL + '/api/courses?limit=50&offset=0');
  checkRes = check(response, {
    'courses status is 200': function(r) { return r.status === 200; },
    'courses response time < 300ms': function(r) { return r.timings.duration < 300; },
    'courses returns data': function(r) { return r.json().length > 0; },
  });
  errorRate.add(!checkRes);
  sleep(2);

  // Test 4: Search Courses
  const searchTerms = ['資料結構', '微積分', '程式設計', 'English', '通識'];
  const randomTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  response = http.get(BASE_URL + '/api/courses?q=' + encodeURIComponent(randomTerm) + '&limit=20');
  checkRes = check(response, {
    'search status is 200': function(r) { return r.status === 200; },
    'search response time < 400ms': function(r) { return r.timings.duration < 400; },
  });
  errorRate.add(!checkRes);
  sleep(1);

  // Test 5: Get Specific Course
  const courseId = Math.floor(Math.random() * 1000) + 1;
  response = http.get(BASE_URL + '/api/courses/' + courseId);
  checkRes = check(response, {
    'get course response time < 200ms': function(r) { return r.timings.duration < 200; },
  });
  if (response.status !== 404) {
    errorRate.add(!checkRes);
  }
  sleep(2);
}
