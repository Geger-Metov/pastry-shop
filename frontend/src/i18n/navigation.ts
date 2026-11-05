import { createNavigation } from "next-intl/navigation";

import { routing } from "./routing";

// Link, redirect, usePathname и useRouter, которые сами добавляют язык в URL.
// Во всём приложении импортируем ссылки отсюда, а не из next/link.
export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);
