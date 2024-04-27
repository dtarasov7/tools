import http from 'k6/http';

export const options = {
  vus: 5,
  duration: '10m',
};


export default function () {
  http.get('http://10.80.');
}
