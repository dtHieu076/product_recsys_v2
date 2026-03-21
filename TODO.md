# Pagination Implementation for Home Page

## Steps:

- [ ] 1. Update backend schemas/product_schema.py (add PaginatedProducts model)
- [ ] 2. Update backend api/product_api.py (add pagination params to GET /products, return paginated dict)
- [ ] 3. Update frontend types/type.ts (add PaginatedResponse interface)
- [ ] 4. Update frontend api/productApi.ts (add getProductsPaginated function)
- [ ] 5. Create components/Pagination.tsx (new pagination UI component)
- [ ] 6. Update pages/Home/HomePage.init.ts (add page state, use paginated API)
- [ ] 7. Update pages/Home/HomePage.tsx (add Pagination below ProductGrid)
- [ ] 8. Test changes: restart backend/frontend, verify on http://localhost:5173/

**Notes:** Page size=12, simple UI with prev/next + page numbers (1-2-3...).
