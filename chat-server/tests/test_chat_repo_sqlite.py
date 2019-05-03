import pytest

from chat_server.services.chat_repository_sqlite import ChatRepositorySqlite


@pytest.mark.integration
def test_user():
    repo = ChatRepositorySqlite('test.db')
    repo.create_user('john.doe@example.com', 'trustno1')
    print('Done')
