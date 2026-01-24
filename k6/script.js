import http from 'k6/http';
import { check } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 1 },
        { duration: '30s', target: 10 },
        { duration: '30s', target: 50 },
        { duration: '30s', target: 100 },
        { duration: '30s', target: 200 },
        { duration: '30s', target: 300 },
        { duration: '30s', target: 400 },
        { duration: '30s', target: 500 },
        { duration: '30s', target: 600 },
        { duration: '30s', target: 700 },
        { duration: '30s', target: 800 },
        { duration: '30s', target: 900 },
        { duration: '30s', target: 1000 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<6000'], // endpoint ~5s
    },
};

export default function () {
    let res = http.get('http://164.90.240.114/work-cpu-bound');
    check(res, { 'status is 200': (r) => r.status === 200 });
}
