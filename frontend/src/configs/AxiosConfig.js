import axios from "axios";

axios.defaults.withCredentials = true;

// eslint-disable-next-line no-undef
const app = axios.create({
 withCredentials: true,
 headers: {
  "accept": "application/json",
  "Content-Type": "application/x-www-form-urlencoded",
 }
});

export const appJSON = axios.create({
 withCredentials: true,
 headers: {
  "accept": "application/json",
  "Content-Type": "application/json",
 }
});

export const appFiles = axios.create({
 withCredentials: true,
 headers: {
  "accept": "application/json",
  "Content-Type": "multipart/form-data"
 }
});


app.interceptors.request.use((config) => {
 return config;
});

/*
  The below is required if you want your API to return
  server message errors. Otherwise, you'll just get
  generic status errors.

  If you use the interceptor below, then make sure you
  return an "err" (or whatever you decide to name it) message
  from your express route:

  res.status(404).json({ err: "You are not authorized to do that." })

*/

export default app;