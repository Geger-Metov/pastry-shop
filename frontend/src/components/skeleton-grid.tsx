/** Заглушка на время загрузки списка (показывается внутри <Suspense fallback>). */
export function SkeletonGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-hidden>
      {Array.from({ length: 6 }, (_, index) => (
        <div key={index} className="bg-muted h-64 animate-pulse rounded-xl" />
      ))}
    </div>
  );
}
