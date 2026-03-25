# Product RecSys Task: Integrate Real API for moduleC (SASRec)

## Steps to Complete:
1. ✅ Add `category_code?: string;` to Product interface in `product_recsys_frontend/src/types/type.ts`
2. ✅ Create `getSASRecRecommendations` function in `product_recsys_frontend/src/api/recommendationApi.ts` (fetch ngrok API)
3. ✅ Update `product_recsys_frontend/src/pages/ModelComparison/ModelComparisonPage.init.ts`: 
   - Add import `getSASRecRecommendations`
   - Remove `useMockForC` and mockModelComparisons usage
   - Fetch modelC with `getSASRecRecommendations(uid)` + mapping like modelB
4. ✅ Task complete: moduleC (SASRec) now uses real ngrok API.

## Testing Command:
```bash
cd product_recsys_frontend && npm run dev
```
Open http://localhost:5173/model-comparison, enter user_id=520088904, click Fetch Data. Verify SASRec column shows real recommendations (Nike Air Max, Apple iPhone, etc.) with confidence scores as % badges.


## Testing Command:
```bash
cd product_recsys_frontend && npm run dev
```
Open http://localhost:5173/model-comparison
