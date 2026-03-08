import type { Pagination as PaginationType } from "../../types/api";

interface PaginationProps {
  pagination: PaginationType;
  onPageChange: (page: number) => void;
}

export function Pagination({ pagination, onPageChange }: PaginationProps) {
  const { current_page, total_pages, total_count, has_prev_page, has_next_page } =
    pagination;

  return (
    <div className="pagination">
      <button
        className="btn btn-sm"
        disabled={!has_prev_page}
        onClick={() => onPageChange(current_page - 1)}
        aria-label="이전 페이지"
      >
        ← 이전
      </button>
      <span>
        {current_page} / {total_pages} 페이지 (총 {total_count}건)
      </span>
      <button
        className="btn btn-sm"
        disabled={!has_next_page}
        onClick={() => onPageChange(current_page + 1)}
        aria-label="다음 페이지"
      >
        다음 →
      </button>
    </div>
  );
}
