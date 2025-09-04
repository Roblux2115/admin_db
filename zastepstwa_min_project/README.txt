
Zastępstwa – PROSTA wersja, tylko dla admina (bez logowania).

Jak uruchomić:
1) python -m venv .venv && .venv\Scripts\activate (Windows) lub source .venv/bin/activate (Linux/Mac)
2) pip install django
3) cd serwer
4) python manage.py migrate
5) python manage.py seed_simple
6) python manage.py runserver
7) Wejdź na http://127.0.0.1:8000/

Widoki:
- "/" (kalendarz) – wybór wykładowcy na górze; kliknięcie zajęć -> formularz dodania zastępstwa
- "/substitutions/new?session_id=ID"

REST (proste JSON):
- GET  /api/lecturers
- GET  /api/events?lecturer_id=<id optional>
- POST /api/substitutions   body: {"session_id":<int>, "lecturer_id":<int>}
- POST /api/mark_needs      body: {"session_id":<int>, "needs":true|false}

Algorytmy w zastepstwa/services.py:
- kwalifikacje przedmiotu vs kwalifikacje wykładowcy
- kolizja czasowa zajęć
- limit zastępstw / tydzień
- limit łącznych godzin nauczania / tydzień

Uwaga: Frontend korzysta z FullCalendar z CDN.


DOKONCZYC MOZLIWOSC

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 1043, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 994, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\autoreload.py", line 64, in wrapper
    fn(*args, **kwargs)
    ~~^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\commands\runserver.py", line 133, in inner_run
    self.check(display_num_errors=True)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\base.py", line 485, in check
    all_issues = checks.run_checks(
        app_configs=app_configs,
    ...<2 lines>...
        databases=databases,
    )
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\registry.py", line 88, in run_checks
    new_errors = check(app_configs=app_configs, databases=databases)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 14, in check_url_config
    return check_resolver(resolver)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 24, in check_resolver
    return check_method()
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 494, in check
    for pattern in self.url_patterns:
                   ^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 715, in url_patterns
    patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
                       ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 708, in urlconf_module
    return import_module(self.urlconf_name)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\serwer\urls.py", line 7, in <module>
    path('', include('zastepstwa.urls')),
             ~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\conf.py", line 38, in include
    urlconf_module = import_module(urlconf_module)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\urls.py", line 4, in <module>
    from . import views
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\views.py", line 27, in <module>
    from .models import Lecturer, Subject, ClassSession, Substitution, LecturerUnavailability
ImportError: cannot import name 'LecturerUnavailability' from 'zastepstwa.models' (C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\models.py)
C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\views.py changed, reloading.
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 1043, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 994, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\autoreload.py", line 64, in wrapper
    fn(*args, **kwargs)
    ~~^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\commands\runserver.py", line 133, in inner_run
    self.check(display_num_errors=True)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\base.py", line 485, in check
    all_issues = checks.run_checks(
        app_configs=app_configs,
    ...<2 lines>...
        databases=databases,
    )
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\registry.py", line 88, in run_checks
    new_errors = check(app_configs=app_configs, databases=databases)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 14, in check_url_config
    return check_resolver(resolver)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 24, in check_resolver
    return check_method()
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 494, in check
    for pattern in self.url_patterns:
                   ^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 715, in url_patterns
    patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
                       ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 708, in urlconf_module
    return import_module(self.urlconf_name)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\serwer\urls.py", line 7, in <module>
    path('', include('zastepstwa.urls')),
             ~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\conf.py", line 38, in include
    urlconf_module = import_module(urlconf_module)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\urls.py", line 4, in <module>
    from . import views
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\views.py", line 28, in <module>
    from .forms import SessionForm
ImportError: cannot import name 'SessionForm' from 'zastepstwa.forms' (C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\forms.py)
C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\views.py changed, reloading.
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 1043, in _bootstrap_inner
    self.run()
    ~~~~~~~~^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\threading.py", line 994, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\autoreload.py", line 64, in wrapper
    fn(*args, **kwargs)
    ~~^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\commands\runserver.py", line 133, in inner_run
    self.check(display_num_errors=True)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\management\base.py", line 485, in check
    all_issues = checks.run_checks(
        app_configs=app_configs,
    ...<2 lines>...
        databases=databases,
    )
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\registry.py", line 88, in run_checks
    new_errors = check(app_configs=app_configs, databases=databases)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 14, in check_url_config
    return check_resolver(resolver)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\core\checks\urls.py", line 24, in check_resolver
    return check_method()
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 494, in check
    for pattern in self.url_patterns:
                   ^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 715, in url_patterns
    patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
                       ^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\utils\functional.py", line 57, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\resolvers.py", line 708, in urlconf_module
    return import_module(self.urlconf_name)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\serwer\urls.py", line 7, in <module>
    path('', include('zastepstwa.urls')),
             ~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\site-packages\django\urls\conf.py", line 38, in include
    urlconf_module = import_module(urlconf_module)
  File "C:\Users\ciast\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\urls.py", line 4, in <module>
    from . import views
  File "C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\views.py", line 27, in <module>
    from .models import Lecturer, Subject, ClassSession, Substitution, LecturerUnavailability
ImportError: cannot import name 'LecturerUnavailability' from 'zastepstwa.models' (C:\Users\ciast\Downloads\zastepstwa_min_project\zastepstwa\models.py)





























