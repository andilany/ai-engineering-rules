+++
id = "data.django-orm"
title = "Django ORM"
severity = "conditional"
scopes = ["python", "django", "data"]
+++
# Django ORM

- Django projects use Django ORM by default unless the existing project deliberately uses another persistence layer.
- Prefer async ORM methods where Django and the database backend provide real async support.
- Avoid bypassing model/transaction invariants with ad-hoc SQL.
