import createClient, { type ClientOptions } from "openapi-fetch";
import type { components, paths } from "./v1";

export type { components, paths } from "./v1";

export type Schemas = components["schemas"];

export type SbtbClient = ReturnType<typeof createClient<paths>>;

export function createSbtbClient(options: ClientOptions): SbtbClient {
  return createClient<paths>(options);
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(`API ${status}: ${detail}`);
    this.name = "ApiError";
  }
}
