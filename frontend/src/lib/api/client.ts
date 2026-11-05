import "server-only";

import createClient from "openapi-fetch";

import type { paths } from "./schema";

function createApi() {
  const baseUrl = process.env.API_URL;
  if (!baseUrl) throw new Error("API_URL is not set");
  return createClient<paths>({ baseUrl });
}

let client: ReturnType<typeof createApi> | undefined;

// Клиент создаётся при первом вызове, а не при импорте файла
export function getApi() {
  client ??= createApi();
  return client;
}
