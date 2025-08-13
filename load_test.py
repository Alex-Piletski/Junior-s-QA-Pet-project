#!/usr/bin/env python3
"""
Нагрузочное тестирование для QA Pet Project
Тестирует производительность приложения под нагрузкой
"""

import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import argparse
from datetime import datetime
import sys

class LoadTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.session = requests.Session()
        
        # Настройки тестов
        self.test_configs = {
            'home_page': {
                'url': '/',
                'method': 'GET',
                'name': 'Главная страница'
            },
            'ping': {
                'url': '/ping',
                'method': 'GET',
                'name': 'Ping endpoint'
            },
            'api_notes': {
                'url': '/api/notes',
                'method': 'GET',
                'name': 'API Notes (GET)'
            },
            'register': {
                'url': '/register',
                'method': 'GET',
                'name': 'Страница регистрации'
            },
            'login': {
                'url': '/login',
                'method': 'GET',
                'name': 'Страница входа'
            }
        }
    
    def make_request(self, test_name, url, method='GET', data=None, headers=None):
        """Выполняет один запрос и возвращает результат"""
        full_url = f"{self.base_url}{url}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(full_url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(full_url, json=data, headers=headers, timeout=10)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # в миллисекундах
            
            return {
                'test_name': test_name,
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'duration_ms': duration,
                'success': response.status_code < 400,
                'response_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            return {
                'test_name': test_name,
                'url': url,
                'method': method,
                'status_code': 0,
                'duration_ms': 10000,  # 10 секунд таймаут
                'success': False,
                'response_size': 0,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'test_name': test_name,
                'url': url,
                'method': method,
                'status_code': 0,
                'duration_ms': 0,
                'success': False,
                'response_size': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_single_test(self, test_name, concurrent_users=1, requests_per_user=1):
        """Запускает тест с указанным количеством пользователей"""
        config = self.test_configs.get(test_name)
        if not config:
            print(f"❌ Неизвестный тест: {test_name}")
            return []
        
        print(f"🚀 Запуск теста: {config['name']}")
        print(f"   Пользователей: {concurrent_users}")
        print(f"   Запросов на пользователя: {requests_per_user}")
        print(f"   Всего запросов: {concurrent_users * requests_per_user}")
        
        results = []
        
        def user_worker():
            user_results = []
            for _ in range(requests_per_user):
                result = self.make_request(
                    test_name, 
                    config['url'], 
                    config['method']
                )
                user_results.append(result)
            return user_results
        
        # Запускаем пользователей параллельно
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_worker) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    user_results = future.result()
                    results.extend(user_results)
                except Exception as e:
                    print(f"❌ Ошибка в потоке: {e}")
        
        return results
    
    def run_all_tests(self, concurrent_users=5, requests_per_user=10):
        """Запускает все тесты"""
        print("🔥 НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
        print("=" * 50)
        print(f"Базовый URL: {self.base_url}")
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        all_results = {}
        
        for test_name in self.test_configs.keys():
            results = self.run_single_test(test_name, concurrent_users, requests_per_user)
            all_results[test_name] = results
            
            # Анализируем результаты
            self.analyze_results(test_name, results)
            print()
        
        # Общий анализ
        self.analyze_all_results(all_results)
        
        return all_results
    
    def analyze_results(self, test_name, results):
        """Анализирует результаты одного теста"""
        if not results:
            print("❌ Нет результатов для анализа")
            return
        
        config = self.test_configs[test_name]
        
        # Фильтруем успешные запросы
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            durations = [r['duration_ms'] for r in successful]
            
            print(f"📊 Результаты теста: {config['name']}")
            print(f"   ✅ Успешных запросов: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
            print(f"   ❌ Неудачных запросов: {len(failed)}")
            print(f"   ⏱️  Время ответа:")
            print(f"      Среднее: {statistics.mean(durations):.2f} мс")
            print(f"      Медиана: {statistics.median(durations):.2f} мс")
            print(f"      Минимум: {min(durations):.2f} мс")
            print(f"      Максимум: {max(durations):.2f} мс")
            print(f"      Стандартное отклонение: {statistics.stdev(durations):.2f} мс")
            
            # RPS (запросов в секунду)
            total_time = max(r['duration_ms'] for r in successful) / 1000
            rps = len(successful) / total_time if total_time > 0 else 0
            print(f"   🚀 RPS (запросов/сек): {rps:.2f}")
            
            # Размер ответа
            avg_size = statistics.mean([r['response_size'] for r in successful])
            print(f"   📦 Средний размер ответа: {avg_size:.0f} байт")
        else:
            print(f"❌ Все запросы неудачны для теста: {config['name']}")
        
        if failed:
            print(f"   🔍 Ошибки:")
            error_counts = {}
            for r in failed:
                error = r.get('error', f"HTTP {r.get('status_code', 'Unknown')}")
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"      {error}: {count} раз")
    
    def analyze_all_results(self, all_results):
        """Анализирует все результаты тестов"""
        print("📈 ОБЩИЙ АНАЛИЗ")
        print("=" * 50)
        
        total_requests = 0
        total_successful = 0
        total_failed = 0
        all_durations = []
        
        for test_name, results in all_results.items():
            total_requests += len(results)
            successful = [r for r in results if r['success']]
            total_successful += len(successful)
            total_failed += len(results) - len(successful)
            all_durations.extend([r['duration_ms'] for r in successful])
        
        print(f"📊 Общая статистика:")
        print(f"   Всего запросов: {total_requests}")
        print(f"   Успешных: {total_successful} ({total_successful/total_requests*100:.1f}%)")
        print(f"   Неудачных: {total_failed} ({total_failed/total_requests*100:.1f}%)")
        
        if all_durations:
            print(f"   ⏱️  Общее время ответа:")
            print(f"      Среднее: {statistics.mean(all_durations):.2f} мс")
            print(f"      Медиана: {statistics.median(all_durations):.2f} мс")
            print(f"      Минимум: {min(all_durations):.2f} мс")
            print(f"      Максимум: {max(all_durations):.2f} мс")
            print(f"      P95: {sorted(all_durations)[int(len(all_durations)*0.95)]:.2f} мс")
            print(f"      P99: {sorted(all_durations)[int(len(all_durations)*0.99)]:.2f} мс")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        if total_failed > 0:
            print(f"   ⚠️  Есть неудачные запросы - проверить стабильность")
        
        if all_durations:
            avg_duration = statistics.mean(all_durations)
            if avg_duration > 1000:
                print(f"   🐌 Медленные ответы (>1с) - оптимизировать производительность")
            elif avg_duration < 100:
                print(f"   ⚡ Отличная производительность (<100мс)")
            else:
                print(f"   ✅ Хорошая производительность")
        
        # Сохраняем результаты
        self.save_results(all_results)
    
    def save_results(self, all_results):
        """Сохраняет результаты в файл"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"load_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'base_url': self.base_url,
                    'results': all_results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Результаты сохранены в: {filename}")
        except Exception as e:
            print(f"❌ Ошибка сохранения результатов: {e}")
    
    def test_rate_limiting(self):
        """Тестирует rate limiting"""
        print("🚦 ТЕСТИРОВАНИЕ RATE LIMITING")
        print("=" * 50)
        
        # Тестируем разные эндпоинты с превышением лимитов
        rate_limit_tests = [
            ('/api/notes', 'GET', 50, 'API Notes Rate Limit'),
            ('/ping', 'GET', 200, 'Ping Rate Limit'),
            ('/register', 'GET', 10, 'Register Rate Limit')
        ]
        
        for url, method, limit, name in rate_limit_tests:
            print(f"\n🔍 Тестируем: {name}")
            print(f"   URL: {url}")
            print(f"   Ожидаемый лимит: {limit} запросов")
            
            results = []
            for i in range(limit + 10):  # Делаем больше запросов чем лимит
                result = self.make_request(f"rate_limit_{url}", url, method)
                results.append(result)
                
                if result['status_code'] == 429:
                    print(f"   ✅ Rate limit сработал на запросе #{i+1}")
                    break
                elif i == limit + 9:
                    print(f"   ⚠️  Rate limit не сработал после {limit + 10} запросов")
            
            # Анализируем результаты
            successful = [r for r in results if r['success']]
            rate_limited = [r for r in results if r['status_code'] == 429]
            
            print(f"   📊 Результаты:")
            print(f"      Успешных: {len(successful)}")
            print(f"      Rate Limited: {len(rate_limited)}")
            print(f"      Ошибок: {len(results) - len(successful) - len(rate_limited)}")

def main():
    parser = argparse.ArgumentParser(description='Нагрузочное тестирование QA Pet Project')
    parser.add_argument('--url', default='http://localhost:5000', help='Базовый URL приложения')
    parser.add_argument('--users', type=int, default=5, help='Количество одновременных пользователей')
    parser.add_argument('--requests', type=int, default=10, help='Запросов на пользователя')
    parser.add_argument('--test', help='Запустить конкретный тест')
    parser.add_argument('--rate-limit', action='store_true', help='Тестировать rate limiting')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url)
    
    try:
        if args.rate_limit:
            tester.test_rate_limiting()
        elif args.test:
            results = tester.run_single_test(args.test, args.users, args.requests)
            tester.analyze_results(args.test, results)
        else:
            tester.run_all_tests(args.users, args.requests)
            
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
