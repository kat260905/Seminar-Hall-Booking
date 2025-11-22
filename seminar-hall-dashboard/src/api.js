import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000", // Flask/FastAPI backend
});

export const fetchBookings = () => API.get("/bookings");
