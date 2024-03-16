# -*- coding: utf-8 -*-
b_scan = u'СКАНИРОВАНИЕ'
b_open = u'Открыть в ДЕМО'
b_select = u'ВЫБОР'
b_find = u'ПОИСК'
b_all_cars = u'ВСЕ АВТО'
b_back = u'<НАЗАД>'
b_stop = u'СТОП'
b_start = u'СТАРТ'
b_log = u'Создание logs'
b_saved = u'Сохранить'
b_clear = u'Сбросить все ОШИБКИ'
b_close = u'ЗАКРЫТЬ'
b_read_dtc = u'<Чтение ошибок DTC>'
b_change_view = u'Сменить вид'
b_lang = u'Русский'
b_savedcar = u'Загрузить savedCAR'
b_quit = u'<ВЫХОД>'
b_write = u'Записать'
b_clear1 = u'ОЧИСТИТЬ'
b_portrait = u'ПОРТРЕТНЫЙ'
b_landscape = u'ЛАНДШАФТНЫЙ'
b_all_prot = u'ВСЕ ПРОТОКОЛЫ'

l_cont1 = u'Выбранный ЭБУ не определен. Пожалуйста, сначала отсканируйте его.'
l_cont2 = u'ELM не отвечает.'
l_cont3 = u'Нет запроса ReadDTC для этого ECU'
l_cont4 = u'Неверный ответ на команду ReadDTC'
l_cont5 = u'Чтение DTC вернуло ошибку'
l_cont6 = u'Нет кода неисправности'
l_cont7 = u'Сканирование:'
l_cont8 = u' Обнаружено: '
l_cont9 = u'ПОИСК DUMP'
l_cont10 = u'ПОИСК XML-ФАЙЛОВ'
l_cont11 = u'Сохранен список ЭБУ с именем saveCAR_'
l_cont12 = u'Вы собираетесь очистить диагностические коды неисправностей.\n Вы уверены, что это то, что вам нужно?'
l_cont13 = u'Пустой экран.'
l_cont14 = u'Выбранный дамп и используемый одинаковые.\n Попробуйте выбрать другой если нужно.'
l_title1 = u'Сканирование '
l_title2 = u'Пожалуйста подтвердите'
l_title3 = u'Выберите дамп'
l_title4 = u'Выберите xml ECU'
l_title5 = u'ПОИСК АВТО'
l_title6 = u'Считанные ошибки'
l_title7 = u'Нет отличий в дампах.'
l_title8 = u'Выбор протокола'
l_text1 = u'Загрузка дампа'
l_text2 = u'Сохранение дампа'
l_text3 = u'ДА'
l_text4 = u'НЕТ'
l_text5 = u'Удаление информации о кодах неисправности'
l_text6 = u'Нет запроса ClearDTC для этого ECU, будет отправлено значение по умолчанию 14FF00.'
l_text7 = u'Произошла ошибка при удалении DTC.\n\n Ошибка удаления DTC.'
l_text8 = u'Удаление DTC успешно выполнено.'
l_text9 = u'Откат DUMP'
l_text10 = u'Ориентация'
l_op_scr = u'Открытие XML-ФАЙЛА'
l_font_size = u'Размер шрифта'
l_font_start = u'Шрифт начального экрана'
l_car = u'АВТО'
l_dump = u'ДАМП'
l_prot = u'Протокол'
l_name = u'Имя'
l_n_car1 = u'Не выбрано авто'
l_n_car2 = u'Не выбрано savedCAR'
l_demo = u'Загрузка в ДЕМО'
l_savedcar = u'Загрузка savedCAR'
l_lang = u'Язык APP'
l_scan = u'Сканирование'
l_load = u'Загрузка'
l_enter_here = u'ENTER'
error = u'ОШИБКА'
not_ident = u'Нет подходящих идентификаторов'
lang = 'en'

list_lang = {
            '01':'АБС',
            '02':'Управл. подв.',
            '04':'Усил. рул. упр.',
            '06':'Блок управл. потребл. энергии',
            '07':'Световые приборы',
            '08':'Пневматические',
            '0B':'BMS 12V',
            '0D':'Стояночный тормоз',
            '0E':'Помощь при парковке',
            '0E':'Помощь при парковке',
            '0F':'Компл "СВОБ. РУКИ"',
            '11':'Система помощи при вождении',
            '13':'Радио',
            '14':'BSG',
            '16':'Блок адаптивного освещения',
            '1A':'Нагреватель',
            '1B':'Блокировка дифференциала',
            '1C':'Блок управления крышей',
            '1E':'Полный привод 4x4',
            '23':'4 управляемых колеса',
            '24':'Пер.датч.обнаруж.преп.',
            '25':'Проверка шасси',
            '26':'ЦЭКБС',
            '27':'Блок защ. и коммутац.',
            '29':'Кондиционер',
            '2A':'Сиденье водителя',
            '2B':'Лазерный радар',
            '2C':'П. БЕЗ./УС. ПР. Н.',
            '2E':'Отсоединенная педаль',
            '32':'СУПЕРВИЗОР или DCDC',
            '37':'Инвертор',
            '3A':'Блок согласования',
            '3C':'Отопитель',
            '3F':'Блок слежения',
            '40':'Проверка линии разметки',
            '41':'Шлюз CAN',
            '47':'Видеорегистратор',
            '4B':'DCU',
            '4D':'Электр. управл. КПП',
            '50':'ТАБЛО/ТАХОМЕТР',
            '51':'Панель приборов (П/ПАН)',
            '52':'Синтез речи',
            '57':'Блок обмена данными',
            '59':'Интерфейс мульт сис',
            '5D':'Блок адаптера щитка приборов',
            '60':'Проектор на вет. ст.',
            '61':'Периферийный обзор',
            '62':'Передняя камера',
            '63':'Задний левый боковой радар',
            '64':'Задний правый боковой радар',
            '65':'Задняя камера',
            '66':'Индикатор зарядки',
            '67':'BCB',
            '68':'PEB',
            '6B':'Опред. слепых зон',
            '6E':'АКП',
            '70':'Разр. лампа',
            '71':'COSLAD лев.',
            '72':'COSLAD прав.',
            '73':'Адаптивное освещение (справа)',
            '77':'Блок упр. тел. сис.',
            '79':'СИС ВП ГАЗ ТОП',
            '7A':'Система впрыска',
            '7B':'Адаптивное освещение (слева)',
            '7C':'АВТ ВКЛ ПРИБ ПЕР ОСВ',
            '81':'Система предупрежд. пешеходов',
            '82':'Индукц. заряд. устр. для тел.',
            '86':'Усилитель',
            '87':'Мультимед соединение',
            '93':'BMS',
            '95':'EVC',
            '97':'Контроллер несущей силы тока',
            '99':'Блок уч автомобиля',
            'A5':'Дверь водителя',
            'A6':'Дверь пассажира',
            'A7':'Дв. задка с сервопр.',
            'A8':'Система защиты BMS',
            'AB':'Модуль виртуального ключа',
            'C0':'Модуль "СВОБ. РУКИ"',
            'D1':'Шлюз БЕЗОПАСНОСТИ',
            'D2':'Канал основной сети CAN',
            'D3':'Модуль управл. сист. мочевины',
            'DF':'Тяговый электродвигатель',
            'E0':'Герметизир. топливный бак',
            'E2':'Вакуумный усил. тормозов',
            'E3':'Стартер-генератор',
            'F7':'Левая дверь/ Сиденье пассажира',
            'F8':'Правая дверь/ Складное сиденье',
            'FE':'Доступ "СВОБ. РУКИ"',
            }