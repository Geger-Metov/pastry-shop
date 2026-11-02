import "server-only";

import createClient from "openapi-fetch";

import type { paths } from "./schema";

if (!process.env.API_URL) throw new Error("API_URL is not set");

export const api = createClient<paths>({
  baseUrl: process.env.API_URL,
});
