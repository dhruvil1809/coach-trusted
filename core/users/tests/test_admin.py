import contextlib
from http import HTTPStatus
from importlib import reload

import pytest
from django.contrib import admin
from django.urls import reverse

from core.users.models import User


class TestUserAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_search(self, admin_client):
        url = reverse("admin:users_user_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == HTTPStatus.OK

    # def test_add(self, admin_client):
    #     url = reverse("admin:users_user_add")  # noqa: ERA001
    #     response = admin_client.get(url)  # noqa: ERA001
    #     assert response.status_code == HTTPStatus.OK  # noqa: ERA001

    #     response = admin_client.post(  # noqa: ERA001, RUF100
    #         url,
    #         data={  # noqa: ERA001, RUF100
    #             "username": "test",  # noqa: ERA001
    #             "password1": "My_R@ndom-P@ssw0rd",  # noqa: ERA001
    #             "password2": "My_R@ndom-P@ssw0rd",  # noqa: ERA001
    #         },
    #     )  # noqa: ERA001, RUF100
    #     assert response.status_code == HTTPStatus.FOUND  # noqa: ERA001
    #     assert User.objects.filter(username="test").exists()  # noqa: ERA001

    def test_view_user(self, admin_client):
        user = User.objects.get(username="admin")
        url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.fixture
    def _force_allauth(self, settings):
        settings.DJANGO_ADMIN_FORCE_ALLAUTH = True
        # Reload the admin module to apply the setting change
        import core.users.admin as users_admin

        with contextlib.suppress(admin.sites.AlreadyRegistered):  # type: ignore[attr-defined]
            reload(users_admin)
