import nicegui.native.native_mode
from nicegui import ui
import json
from typing import List, Dict
import soil_crop_matcher


def load_data():
    """Загрузка данных из JSON-файлов"""
    with open('soils.json', 'r', encoding='utf-8') as f:
        soils = json.load(f)
    with open('crops.json', 'r', encoding='utf-8') as f:
        crops = json.load(f)
    with open('results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    return soils, crops, results

def create_soil_card(soil: Dict):
    """Создание карточки для почвы"""
    with ui.card().tight().classes('h-full'):
        ui.label(soil['name']).classes('text-h6 bg-blue-100 p-2')
        with ui.card_section():
            ui.label(f"Кислотность: {soil['acidity']}")
            ui.label(f"Влажность: {soil['moisture']}")
            ui.label(f"Гумус: {soil['humus']}%")
            ui.label(f"Структура: {soil['structure']}")
            with ui.expansion('Макроэлементы', icon='nutrition').classes('w-full'):
                ui.label(f"Азот: {soil['macros']['nitrogen']}")
                ui.label(f"Фосфор: {soil['macros']['phosphorus']}")
                ui.label(f"Калий: {soil['macros']['potassium']}")
                ui.label(f"Магний: {soil['macros']['magnesium']}")
                ui.label(f"Кальций: {soil['macros']['calcium']}")

def create_crop_card(crop: Dict):
    """Создание карточки для культуры"""
    with ui.card().tight().classes('h-full'):
        ui.label(crop['name']).classes('text-h6 bg-green-100 p-2')
        with ui.card_section():
            ui.label(f"Требуемая кислотность: {crop['required_acidity']}")
            ui.label(f"Требуемая влажность: {crop['required_moisture']}")
            ui.label(f"Требуемый гумус: {crop['required_humus']}%")
            ui.label(f"Предпочтительная структура: {crop['preferred_structure']}")
            with ui.expansion('Требуемые макроэлементы', icon='nutrition').classes('w-full'):
                ui.label(f"Азот: {crop['required_macros']['nitrogen']}")
                ui.label(f"Фосфор: {crop['required_macros']['phosphorus']}")
                ui.label(f"Калий: {crop['required_macros']['potassium']}")
                ui.label(f"Магний: {crop['required_macros']['magnesium']}")
                ui.label(f"Кальций: {crop['required_macros']['calcium']}")

def create_result_card(result: Dict, soils: List[Dict], crops: List[Dict]):
    """Создание карточки с результатом подбора"""
    soil = next(s for s in soils if s['name'] == result['best_soil'])
    crop = next(c for c in crops if c['name'] == result['culture'])
    with ui.card().tight().classes('h-full'):
        with ui.row().classes('w-full bg-purple-100 p-2 items-center'):
            ui.label(f"{result['culture']}").classes('text-h6')
            ui.icon('arrow_forward', size='sm')
            ui.label(f"{result['best_soil']}").classes('text-h6')
        with ui.card_section():
            ui.label(f"Мера соответствия: {result['distance']:.2f}")
            ui.label(f"Кислотность: {soil['acidity']} (требуется: {crop['required_acidity']})")
            ui.label(f"Влажность: {soil['moisture']} (требуется: {crop['required_moisture']})")
            ui.label(f"Гумус: {soil['humus']}% (требуется: {crop['required_humus']}%)")

# Загрузка данных
soils, crops, results = load_data()

# Настройка страницы
ui.page_title('Подбор почв для культур')

# Состояния для сортировки
sort_soils_asc = True
sort_crops_asc = True
sort_results_asc = True

# Функции сортировки
def sort_soils():
    global sort_soils_asc
    sort_soils_asc = not sort_soils_asc
    soils_container.clear()
    display_soils()

def sort_crops():
    global sort_crops_asc
    sort_crops_asc = not sort_crops_asc
    crops_container.clear()
    display_crops()

def sort_results():
    global sort_results_asc
    sort_results_asc = not sort_results_asc
    results_container.clear()
    display_results()


# Функции отображения с фильтрацией
def display_soils():
    search_term = soil_search.value.lower()
    filtered = [s for s in soils if search_term in s['name'].lower()]
    sorted_soils = sorted(filtered, key=lambda x: x['name'], reverse=not sort_soils_asc)

    with soils_container:
        if not sorted_soils:
            ui.label('Ничего не найдено').classes('text-lg col-span-2 text-center')
        else:
            for soil in sorted_soils:
                create_soil_card(soil)


def display_crops():
    search_term = crop_search.value.lower()
    filtered = [c for c in crops if search_term in c['name'].lower()]
    sorted_crops = sorted(filtered, key=lambda x: x['name'], reverse=not sort_crops_asc)

    with crops_container:
        if not sorted_crops:
            ui.label('Ничего не найдено').classes('text-lg col-span-2 text-center')
        else:
            for crop in sorted_crops:
                create_crop_card(crop)


def display_results():
    search_term = result_search.value.lower()
    filtered = [r for r in results if (search_term in r['culture'].lower() or
                                       search_term in r['best_soil'].lower())]
    sorted_results = sorted(filtered, key=lambda x: x['culture'], reverse=not sort_results_asc)

    with results_container:
        if not sorted_results:
            ui.label('Ничего не найдено').classes('text-lg w-full text-center')
        else:
            for result in sorted_results:
                create_result_card(result, soils, crops)


# Вкладки
with ui.tabs().classes('w-full') as tabs:
    soils_tab = ui.tab('Почвы')
    crops_tab = ui.tab('Культуры')
    results_tab = ui.tab('Результаты подбора')

with ui.tab_panels(tabs, value=results_tab).classes('w-full'):
    # Вкладка с почвами
    with ui.tab_panel(soils_tab):
        with ui.row().classes('w-full items-center justify-between'):
            soil_search = ui.input('Поиск почв', on_change=display_soils) \
                .props('clearable dense') \
                .classes('w-64')
            ui.button('Сортировать по названию', on_click=sort_soils) \
                .props('icon=sort') \
                .classes('ml-auto')

        soils_container = ui.grid(columns=2).classes('w-full gap-4 mt-4')
        display_soils()

    # Вкладка с культурами
    with ui.tab_panel(crops_tab):
        with ui.row().classes('w-full items-center justify-between'):
            crop_search = ui.input('Поиск культур', on_change=display_crops) \
                .props('clearable dense') \
                .classes('w-64')
            ui.button('Сортировать по названию', on_click=sort_crops) \
                .props('icon=sort') \
                .classes('ml-auto')

        crops_container = ui.grid(columns=2).classes('w-full gap-4 mt-4')
        display_crops()

    # Вкладка с результатами
    with ui.tab_panel(results_tab):
        with ui.row().classes('w-full items-center justify-between'):
            result_search = ui.input('Поиск по культурам или почвам', on_change=display_results) \
                .props('clearable dense') \
                .classes('w-64')
            ui.button('Сортировать по культуре', on_click=sort_results) \
                .props('icon=sort') \
                .classes('ml-auto')

        results_container = ui.column().classes('w-full gap-4 mt-4')
        display_results()

ui.run(reload=False, port=nicegui.native.native_mode.find_open_port())