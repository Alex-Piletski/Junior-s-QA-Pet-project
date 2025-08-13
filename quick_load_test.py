#!/usr/bin/env python3
"""
Быстрое нагрузочное тестирование
Простой скрипт для проверки производительности
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

def test_endpoint(url, method='GET', timeout=5):
    """Тестирует один эндпоинт"""
    start_time = time.time()
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, timeout=timeout)
        
        duration = (time.time() - start_time) * 1000
        return {
            'status_code': response.status_code,
            'duration_ms': duration,
            'success': response.status_code < 400,
            'size': len(response.content)
        }
    except Exception as e:
        return {
            'status_code': 0,
            'duration_ms': 0,
            'success': False,
            'error': str(e)
        }

def load_test(base_url, endpoint, concurrent_users=10, requests_per_user=5):
    """Проводит нагрузочное тестирование"""
    url = f"{base_url}{endpoint}"
    
    print(f"🚀 Тестируем: {endpoint}")
    print(f"   URL: {url}")
    print(f"   Пользователей: {concurrent_users}")
    print(f"   Запросов на пользователя: {requests_per_user}")
    print(f"   Всего запросов: {concurrent_users * requests_per_user}")
    
    results = []
    
    def worker():
        user_results = []
        for _ in range(requests_per_user):
            result = test_endpoint(url)
            user_results.append(result)
        return user_results
    
    # Запускаем тесты параллельно
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(worker) for _ in range(concurrent_users)]
        
        for future in futures:
            try:
                user_results = future.result()
                results.extend(user_results)
            except Exception as e:
                print(f"❌ Ошибка в потоке: {e}")
    
    return results

def analyze_results(endpoint, results):
    """Анализирует результаты тестирования"""
    if not results:
        print("❌ Нет результатов")
        return
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 Результаты для {endpoint}:")
    print(f"   ✅ Успешных: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"   ❌ Неудачных: {len(failed)}")
    
    if successful:
        durations = [r['duration_ms'] for r in successful]
        sizes = [r['size'] for r in successful]
        
        print(f"   ⏱️  Время ответа:")
        print(f"      Среднее: {statistics.mean(durations):.2f} мс")
        print(f"      Медиана: {statistics.median(durations):.2f} мс")
        print(f"      Минимум: {min(durations):.2f} мс")
        print(f"      Максимум: {max(durations):.2f} мс")
        
        # RPS
        total_time = max(durations) / 1000
        rps = len(successful) / total_time if total_time > 0 else 0
        print(f"   🚀 RPS: {rps:.2f} запросов/сек")
        
        print(f"   📦 Размер ответа: {statistics.mean(sizes):.0f} байт")
    
    if failed:
        print(f"   🔍 Ошибки:")
        error_counts = {}
        for r in failed:
            error = r.get('error', f"HTTP {r.get('status_code', 'Unknown')}")
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in error_counts.items():
            print(f"      {error}: {count} раз")

def main():
    base_url = "http://localhost:5000"
    
    # Тестируемые эндпоинты
    endpoints = [
        '/',
        '/ping',
        '/register',
        '/login'
    ]
    
    print("🔥 БЫСТРОЕ НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 50)
    print(f"Базовый URL: {base_url}")
    print(f"Время: {time.strftime('%H:%M:%S')}")
    print()
    
    all_results = {}
    
    for endpoint in endpoints:
        results = load_test(base_url, endpoint, concurrent_users=5, requests_per_user=10)
        all_results[endpoint] = results
        analyze_results(endpoint, results)
        print()
    
    # Общий анализ
    print("📈 ОБЩИЙ АНАЛИЗ")
    print("=" * 50)
    
    total_requests = sum(len(results) for results in all_results.values())
    total_successful = sum(len([r for r in results if r['success']]) for results in all_results.values())
    all_durations = []
    
    for results in all_results.values():
        all_durations.extend([r['duration_ms'] for r in results if r['success']])
    
    print(f"📊 Общая статистика:")
    print(f"   Всего запросов: {total_requests}")
    print(f"   Успешных: {total_successful} ({total_successful/total_requests*100:.1f}%)")
    print(f"   Неудачных: {total_requests - total_successful}")
    
    if all_durations:
        print(f"   ⏱️  Общее время ответа:")
        print(f"      Среднее: {statistics.mean(all_durations):.2f} мс")
        print(f"      Медиана: {statistics.median(all_durations):.2f} мс")
        print(f"      P95: {sorted(all_durations)[int(len(all_durations)*0.95)]:.2f} мс")
    
    print(f"\n✅ Тестирование завершено!")

if __name__ == '__main__':
    main()
