# README_PATCH03

Примеры проверки RBAC:

```bash
# 401: нет токена
curl -i http://localhost:8000/api/v1/bonus

# 403: роль не подходит
curl -i -H "Authorization: Bearer $PROMOTER_TOKEN" \
  http://localhost:8000/api/v1/bonus

# 200: всё ок
curl -i -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/bonus
```
