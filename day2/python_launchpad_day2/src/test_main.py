import unittest
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Импортируем из main.py
from main import (
    Base, User, Client, Ticket, Comment,
    UserRepository, TicketRepository,
    AuthService, TicketService
)

# ==========================================
# НАСТРОЙКА ТЕСТОВОЙ БД
# ==========================================
TEST_DATABASE_URL = "sqlite:///:memory:"  # База в памяти для тестов

class TestBase(unittest.TestCase):
    """Базовый класс для всех тестов"""
    
    @classmethod
    def setUpClass(cls):
        """Создаем тестовую БД один раз для всех тестов"""
        cls.engine = create_engine(TEST_DATABASE_URL, echo=False)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)
    
    def setUp(self):
        """Перед каждым тестом создаем новую сессию"""
        self.session = self.Session()
    
    def tearDown(self):
        """После каждого теста очищаем сессию"""
        self.session.close()

# ==========================================
# ТЕСТЫ МОДЕЛЕЙ БД
# ==========================================
class TestUserModel(TestBase):
    """Тесты модели User"""
    
    def test_create_user(self):
        """Тест создания пользователя"""
        user = User(username="testuser", password="pass123", role="Operator")
        self.session.add(user)
        self.session.commit()
        
        result = self.session.query(User).filter_by(username="testuser").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.role, "Operator")
    
    def test_user_unique_username(self):
        """Тест уникальности имени пользователя"""
        user1 = User(username="unique", password="pass1")
        user2 = User(username="unique", password="pass2")
        self.session.add(user1)
        self.session.commit()
        
        self.session.add(user2)
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_user_default_role(self):
        """Тест роли по умолчанию"""
        user = User(username="user", password="pass")
        self.assertEqual(user.role, "Operator")
    
    def test_user_password_stored(self):
        """Тест что пароль сохраняется"""
        user = User(username="user", password="secret123")
        self.session.add(user)
        self.session.commit()
        
        result = self.session.query(User).first()
        self.assertEqual(result.password, "secret123")


class TestClientModel(TestBase):
    """Тесты модели Client"""
    
    def test_create_client(self):
        """Тест создания клиента"""
        client = Client(name="John Doe", phone="+79991234567")
        self.session.add(client)
        self.session.commit()
        
        result = self.session.query(Client).filter_by(name="John Doe").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.phone, "+79991234567")
    
    def test_client_name_required(self):
        """Тест что имя клиента обязательно"""
        client = Client(name=None, phone="+79991234567")
        self.session.add(client)
        
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_client_without_phone(self):
        """Тест создания клиента без телефона"""
        client = Client(name="Jane Doe", phone=None)
        self.session.add(client)
        self.session.commit()
        
        result = self.session.query(Client).filter_by(name="Jane Doe").first()
        self.assertIsNotNone(result)
        self.assertIsNone(result.phone)


class TestTicketModel(TestBase):
    """Тесты модели Ticket"""
    
    def test_create_ticket(self):
        """Тест создания тикета"""
        ticket = Ticket(title="Issue", description="Description")
        self.session.add(ticket)
        self.session.commit()
        
        result = self.session.query(Ticket).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Issue")
        self.assertEqual(result.status, "Новый")
    
    def test_ticket_default_status(self):
        """Тест статуса по умолчанию"""
        ticket = Ticket(title="Test", description="Desc")
        self.assertEqual(ticket.status, "Новый")
    
    def test_ticket_has_created_at(self):
        """Тест наличия времени создания"""
        ticket = Ticket(title="Test", description="Desc")
        self.session.add(ticket)
        self.session.commit()
        
        result = self.session.query(Ticket).first()
        self.assertIsNotNone(result.created_at)
        self.assertIsInstance(result.created_at, datetime)
    
    def test_ticket_title_required(self):
        """Тест что заголовок тикета обязателен"""
        ticket = Ticket(title=None, description="Desc")
        self.session.add(ticket)
        
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_ticket_description_optional(self):
        """Тест что описание опционально"""
        ticket = Ticket(title="Test", description=None)
        self.session.add(ticket)
        self.session.commit()
        
        result = self.session.query(Ticket).first()
        self.assertIsNone(result.description)


class TestCommentModel(TestBase):
    """Тесты модели Comment"""
    
    def test_create_comment(self):
        """Тест создания комментария"""
        ticket = Ticket(title="Test", description="Desc")
        self.session.add(ticket)
        self.session.commit()
        
        comment = Comment(ticket_id=ticket.id, text="Test comment")
        self.session.add(comment)
        self.session.commit()
        
        result = self.session.query(Comment).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.text, "Test comment")
        self.assertEqual(result.ticket_id, ticket.id)
    
    def test_comment_without_text(self):
        """Тест создания комментария без текста"""
        ticket = Ticket(title="Test", description="Desc")
        self.session.add(ticket)
        self.session.commit()
        
        comment = Comment(ticket_id=ticket.id, text=None)
        self.session.add(comment)
        self.session.commit()
        
        result = self.session.query(Comment).first()
        self.assertIsNone(result.text)

# ==========================================
# ТЕСТЫ РЕПОЗИТОРИЕВ
# ==========================================
class TestUserRepository(TestBase):
    """Тесты UserRepository"""
    
    def test_get_by_username(self):
        """Тест получения пользователя по имени"""
        user = User(username="admin", password="admin")
        self.session.add(user)
        self.session.commit()
        
        repo = UserRepository(self.session)
        result = repo.get_by_username("admin")
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "admin")
    
    def test_get_by_username_not_found(self):
        """Тест получения несуществующего пользователя"""
        repo = UserRepository(self.session)
        result = repo.get_by_username("nonexistent")
        self.assertIsNone(result)
    
    def test_create_default_user_if_not_exists(self):
        """Тест создания пользователя по умолчанию"""
        repo = UserRepository(self.session)
        repo.create_default_user_if_not_exists()
        
        result = self.session.query(User).filter_by(username="admin").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "admin")
        self.assertEqual(result.password, "admin")
        self.assertEqual(result.role, "Администратор")
    
    def test_create_default_user_only_once(self):
        """Тест что пользователь создается только один раз"""
        repo = UserRepository(self.session)
        repo.create_default_user_if_not_exists()
        repo.create_default_user_if_not_exists()
        
        count = self.session.query(User).filter_by(username="admin").count()
        self.assertEqual(count, 1)
    
    def test_get_by_username_case_sensitive(self):
        """Тест что поиск по имени чувствителен к регистру"""
        user = User(username="Admin", password="pass")
        self.session.add(user)
        self.session.commit()
        
        repo = UserRepository(self.session)
        result = repo.get_by_username("admin")
        self.assertIsNone(result)


class TestTicketRepository(TestBase):
    """Тесты TicketRepository"""
    
    def test_get_all(self):
        """Тест получения всех тикетов"""
        ticket1 = Ticket(title="Ticket 1", description="Desc 1")
        ticket2 = Ticket(title="Ticket 2", description="Desc 2")
        self.session.add_all([ticket1, ticket2])
        self.session.commit()
        
        repo = TicketRepository(self.session)
        result = repo.get_all()
        self.assertEqual(len(result), 2)
    
    def test_get_all_empty(self):
        """Тест получения пустого списка тикетов"""
        repo = TicketRepository(self.session)
        result = repo.get_all()
        self.assertEqual(len(result), 0)
    
    def test_create_ticket(self):
        """Тест создания тикета через репозиторий"""
        repo = TicketRepository(self.session)
        ticket = repo.create("New Ticket", "Description")
        
        result = self.session.query(Ticket).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "New Ticket")
    
    def test_create_returns_ticket_object(self):
        """Тест что create возвращает объект тикета"""
        repo = TicketRepository(self.session)
        ticket = repo.create("Test", "Desc")
        
        self.assertIsInstance(ticket, Ticket)
        self.assertEqual(ticket.title, "Test")
    
    def test_get_all_ordered_by_id(self):
        """Тест что тикеты возвращаются в порядке создания"""
        repo = TicketRepository(self.session)
        repo.create("First", "Desc 1")
        repo.create("Second", "Desc 2")
        repo.create("Third", "Desc 3")
        
        result = repo.get_all()
        self.assertEqual(result[0].title, "First")
        self.assertEqual(result[1].title, "Second")
        self.assertEqual(result[2].title, "Third")

# ==========================================
# ТЕСТЫ СЕРВИСОВ
# ==========================================
class TestAuthService(TestBase):
    """Тесты AuthService"""
    
    def setUp(self):
        super().setUp()
        user = User(username="admin", password="admin123")
        self.session.add(user)
        self.session.commit()
    
    def test_login_success(self):
        """Тест успешной авторизации"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        result = auth_svc.login("admin", "admin123")
        self.assertTrue(result)
        self.assertIsNotNone(auth_svc.current_user)
        self.assertEqual(auth_svc.current_user.username, "admin")
    
    def test_login_wrong_password(self):
        """Тест авторизации с неправильным паролем"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        result = auth_svc.login("admin", "wrongpass")
        self.assertFalse(result)
        self.assertIsNone(auth_svc.current_user)
    
    def test_login_nonexistent_user(self):
        """Тест авторизации несуществующего пользователя"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        result = auth_svc.login("nonexistent", "pass")
        self.assertFalse(result)
        self.assertIsNone(auth_svc.current_user)
    
    def test_current_user_initially_none(self):
        """Тест что текущий пользователь изначально None"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        self.assertIsNone(auth_svc.current_user)
    
    def test_login_empty_username(self):
        """Тест авторизации с пустым именем"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        result = auth_svc.login("", "admin123")
        self.assertFalse(result)
    
    def test_login_empty_password(self):
        """Тест авторизации с пустым паролем"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        result = auth_svc.login("admin", "")
        self.assertFalse(result)
    
    def test_login_multiple_times(self):
        """Тест что можно авторизоваться несколько раз"""
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        
        auth_svc.login("admin", "admin123")
        first_user = auth_svc.current_user
        
        # Перезагружаем и логиним снова
        auth_svc.current_user = None
        auth_svc.login("admin", "admin123")
        second_user = auth_svc.current_user
        
        self.assertEqual(first_user.username, second_user.username)


class TestTicketService(TestBase):
    """Тесты TicketService"""
    
    def setUp(self):
        super().setUp()
        self.repo = TicketRepository(self.session)
        self.svc = TicketService(self.repo)
    
    def test_get_all_tickets(self):
        """Тест получения всех тикетов"""
        self.repo.create("Ticket 1", "Desc 1")
        self.repo.create("Ticket 2", "Desc 2")
        
        result = self.svc.get_all_tickets()
        self.assertEqual(len(result), 2)
    
    def test_create_ticket_success(self):
        """Тест успешного создания тикета"""
        ticket = self.svc.create_ticket("New Ticket", "Description")
        
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.title, "New Ticket")
    
    def test_create_ticket_empty_title(self):
        """Тест создания тикета с пустым заголовком"""
        with self.assertRaises(ValueError):
            self.svc.create_ticket("", "Description")
    
    def test_create_ticket_whitespace_title(self):
        """Тест создания тикета с заголовком из пробелов"""
        with self.assertRaises(ValueError):
            self.svc.create_ticket("   ", "Description")
    
    def test_create_ticket_valid_with_empty_description(self):
        """Тест создания тикета с пустым описанием"""
        ticket = self.svc.create_ticket("Valid Title", "")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.description, "")
    
    def test_create_ticket_error_message(self):
        """Тест что сообщение об ошибке правильное"""
        with self.assertRaises(ValueError) as context:
            self.svc.create_ticket("", "Desc")
        
        self.assertEqual(str(context.exception), "Заголовок не может быть пустым")
    
    def test_get_all_tickets_empty(self):
        """Тест получения пустого списка"""
        result = self.svc.get_all_tickets()
        self.assertEqual(len(result), 0)
    
    def test_create_ticket_with_long_description(self):
        """Тест создания тикета с длинным описанием"""
        long_desc = "A" * 1000
        ticket = self.svc.create_ticket("Title", long_desc)
        
        self.assertEqual(ticket.description, long_desc)
    
    def test_create_multiple_tickets(self):
        """Тест создания нескольких тикетов"""
        for i in range(5):
            self.svc.create_ticket(f"Ticket {i}", f"Desc {i}")
        
        result = self.svc.get_all_tickets()
        self.assertEqual(len(result), 5)

# ==========================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ==========================================
class TestIntegration(TestBase):
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # 1. Создаем пользователя
        user_repo = UserRepository(self.session)
        user_repo.create_default_user_if_not_exists()
        
        # 2. Авторизуемся
        auth_svc = AuthService(user_repo)
        login_result = auth_svc.login("admin", "admin")
        self.assertTrue(login_result)
        
        # 3. Создаем тикеты
        ticket_repo = TicketRepository(self.session)
        ticket_svc = TicketService(ticket_repo)
        
        ticket1 = ticket_svc.create_ticket("Issue 1", "Desc 1")
        ticket2 = ticket_svc.create_ticket("Issue 2", "Desc 2")
        
        # 4. Получаем все тикеты
        all_tickets = ticket_svc.get_all_tickets()
        self.assertEqual(len(all_tickets), 2)
        
        # 5. Проверяем данные
        self.assertEqual(all_tickets[0].title, "Issue 1")
        self.assertEqual(all_tickets[1].title, "Issue 2")
    
    def test_multiple_users_and_tickets(self):
        """Тест работы с несколькими пользователями и тикетами"""
        # Создаем пользователей
        user1 = User(username="user1", password="pass1", role="Operator")
        user2 = User(username="user2", password="pass2", role="Manager")
        self.session.add_all([user1, user2])
        self.session.commit()
        
        # Создаем тикеты
        ticket_repo = TicketRepository(self.session)
        for i in range(5):
            ticket_repo.create(f"Ticket {i}", f"Description {i}")
        
        # Проверяем
        users = self.session.query(User).all()
        tickets = ticket_repo.get_all()
        
        self.assertEqual(len(users), 2)
        self.assertEqual(len(tickets), 5)
    
    def test_create_ticket_after_login(self):
        """Тест создания тикета после авторизации"""
        # Авторизуемся
        user_repo = UserRepository(self.session)
        user_repo.create_default_user_if_not_exists()
        auth_svc = AuthService(user_repo)
        auth_svc.login("admin", "admin")
        
        # Создаем тикет
        ticket_repo = TicketRepository(self.session)
        ticket_svc = TicketService(ticket_repo)
        ticket = ticket_svc.create_ticket("Support Request", "Need help")
        
        # Проверяем
        self.assertIsNotNone(auth_svc.current_user)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.status, "Новый")

# ==========================================
# ТЕСТЫ ВАЛИДАЦИИ И ОБРАБОТКИ ОШИБОК
# ==========================================
class TestValidationAndErrors(TestBase):
    """Тесты валидации и обработки ошибок"""
    
    def test_ticket_title_cannot_be_none(self):
        """Тест что заголовок тикета не может быть None"""
        ticket = Ticket(title=None, description="Desc")
        self.session.add(ticket)
        
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_user_username_cannot_be_none(self):
        """Тест что имя пользователя не может быть None"""
        user = User(username=None, password="pass")
        self.session.add(user)
        
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_user_password_cannot_be_none(self):
        """Тест что пароль не может быть None"""
        user = User(username="user", password=None)
        self.session.add(user)
        
        with self.assertRaises(Exception):
            self.session.commit()
    
    def test_ticket_service_validation(self):
        """Тест валидации в сервисе тикетов"""
        ticket_repo = TicketRepository(self.session)
        ticket_svc = TicketService(ticket_repo)
        
        # Пустой заголовок
        with self.assertRaises(ValueError):
            ticket_svc.create_ticket("", "Desc")
        
        # Только пробелы
        with self.assertRaises(ValueError):
            ticket_svc.create_ticket("   \t\n", "Desc")

# ==========================================
# ТЕСТЫ ГРАНИЧНЫХ СЛУЧАЕВ
# ==========================================
class TestEdgeCases(TestBase):
    """Тесты граничных случаев"""
    
    def test_ticket_with_special_characters(self):
        """Тест тикета со специальными символами"""
        ticket_repo = TicketRepository(self.session)
        ticket_svc = TicketService(ticket_repo)
        
        special_title = "Тестик! @#$%^&*() 🎉"
        ticket = ticket_svc.create_ticket(special_title, "Description")
        
        self.assertEqual(ticket.title, special_title)
    
    def test_ticket_with_very_long_title(self):
        """Тест тикета с очень длинным заголовком"""
        ticket_repo = TicketRepository(self.session)
        ticket_svc = TicketService(ticket_repo)
        
        long_title = "A" * 500
        ticket = ticket_svc.create_ticket(long_title, "Desc")
        
        self.assertEqual(ticket.title, long_title)
    
    def test_user_with_numeric_password(self):
        """Тест пользователя с числовым паролем"""
        user = User(username="user", password="123456")
        self.session.add(user)
        self.session.commit()
        
        repo = UserRepository(self.session)
        auth_svc = AuthService(repo)
        result = auth_svc.login("user", "123456")
        
        self.assertTrue(result)
    
    def test_many_comments_for_one_ticket(self):
        """Тест много комментариев для одного тикета"""
        ticket = Ticket(title="Test", description="Desc")
        self.session.add(ticket)
        self.session.commit()
        
        for i in range(100):
            comment = Comment(ticket_id=ticket.id, text=f"Comment {i}")
            self.session.add(comment)
        
        self.session.commit()
        
        comments = self.session.query(Comment).filter_by(ticket_id=ticket.id).all()
        self.assertEqual(len(comments), 100)

# ==========================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# ==========================================
if __name__ == '__main__':
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ АРМ КОНТАКТНОГО ЦЕНТРА")
    print("=" * 70)
    print()
    
    # Запускаем тесты с подробным выводом
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим статистику
    print()
    print("=" * 70)
    print(f"ВСЕГО ТЕСТОВ: {result.testsRun}")
    print(f"УСПЕШНЫХ: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"ОШИБОК: {len(result.errors)}")
    print(f"ПРОВАЛОВ: {len(result.failures)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
