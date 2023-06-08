from argparse import Namespace
from cgi import print_directory, print_form
from math import fabs
from posixpath import split
from re import T
import numpy as np
import investpy as inv
import json
from time import sleep
from threading import Thread
import keyboard as keyb

######################################
rec = "markus02012@yandex.ru"

def main():#  Функция выбора между всеми функциями программы
    exit = False
    
    while exit != True:# проверка на прерывание
        enter_1 = input('\nSelect the next program step: \n0 - Start monitoring and analysis \n1 - Neural network training \n2 - Add one example \n3 - Add some examples \n4 - Delete one example \n5 - Delete some examples \n6 - Delete all examples \n7 - Show examples \n8 - Add new name stock in list \nemail - Change email notification \n9 - Exit \nEnter: ')
        if enter_1 == '0':
            print("\n|__ INSTRUCTION __|\nProgram is work in period 09:40-23:40 at o'clock UTC+0 in working day\nEnter button 'ESC', to cancel operation monitoring\n")
            sleep(5)
            t1 = Thread(target=key_esc)
            t1.start()
            proverkaRSI()
        elif enter_1 == '1':
            neural_network_manager()
        elif enter_1 == '2':
            add_example()
        elif enter_1 == '3':
            add_some_examples()
        elif enter_1 == '4':
            del_one_example()
        elif enter_1 == '5':
            del_some_examples()
        elif enter_1 == '6':
            del_all_examples()
        elif enter_1 == '7':
            show_list_examples()
        elif enter_1 == '8':
            add_new_stock()
        elif enter_1 == 'email':
            recipient_email()
        elif enter_1 == '9':
            exit = True

###################################### "ESC"

def key_esc():# По кнопке "ESC" выходит из цикла, идёт отдельным потоком
    global exit_radius
    exit_radius = False
    keyb.wait('esc')
    print('Cancel a process!!! Wait a few seconds...')
    exit_radius = True
    return exit_radius

###################################### Изменение почты на которую будут высылаться уведомления

def recipient_email():
    global rec
    print('Using now email: ', rec)
    rec_change = input('\nEnter for notification, 0 - default email, 1 - new email: ')
    if rec_change == '1':
        rec = input('\nEnter new email: ')
    else:
        rec = ""
    return rec

###################################### Уведомление о изменение в котировке

def birzha_notification(stock_name, progress_network): # функцмя уведомлеяет через сервер почты
    import smtplib
    num_strin = round(progress_network*100, 5)
    message = f'BUY stock: {stock_name} /_ Probability: {num_strin}% _/'
    sender = ""
    global rec
    recipient = rec
    password = ""

    server = smtplib.SMTP("smtp.yandex.ru", 587)
    server.starttls()

    try:
        server.login(sender, password)
        server.sendmail(sender, recipient, f"From: {sender}\nSubject: Activity stock: {stock_name} !!!\n\n{message}")
    except:
        return print('Error login/password')

###################################### Добавление нескольких примеров в список

def add_some_examples():# Добавление группы примеров
    ds = input('Enter, Add examples by hand - 0\nAdd examples of file - 1\nEnter: ')
    if ds == '0':
        stop_func = 1
        while stop_func != 0:
            stop_func = add_example()
            sleep(2)
    
    elif ds == '1':
        print('\n|__ INSTRUCTION __|\n-Open file in directory program "on_stocks.txt"\n-Write example periods exchange activity in file, for example:\n14/07/2021-0-rsti\n02/07/2021-1-rsti\n28/06/2021-0-rsti\n11/06/2021-1-rsti\n09/06/2021-0-rsti\n')
        yn = input('\nAgree in open/read/write/save of file, y - YES, n - NO\nEnter: ')
        if yn == 'y':
            f = open('on_stocks.txt', 'r')
            rid = f.read()

            rid = rid.split('\n')
            print(rid)
            ext = []
            for i in rid:
                if i == '%':
                    continue
                ext.append(i)
            for p in ext:
                add_example(right_ex=False, ex=p)
            
            f = open('on_stocks.txt', 'w')# Стирает содержимое файла перезаписью
            f.close()
    
    else:
        print('Try again!!!')
    
################################################################# Добавление одного примера в список

def add_example(right_ex=True, ex=''):# Добавление примера периода в список для тренировки
    try:#  Проверка на ошибку во время ввода символов
       print('|__ INSTRUCTION __|\n-Write word "stop", to stop\n-Write word "list", to show list periods stocks')
       f = open('Days_14_example.json', 'r')
       if right_ex == True:
            ex = input('\nEnter data: \n-End period of exchange activity \n-Negative - 0 /Positive - 1 \n-id stock \nFor example (16/05/2019-0-25) or (16/05/2019-0-rual) period for 14 Days : ')
       else:
            print('\nAuto enter example : ', ex)
       if ex == 'stop':# Прерывет функцию при слове 'stop'
           return 0
       elif ex == 'list':# показывает список сразу перед функцией если нужно
           show_list_examples()
       str_popolam = ex.split('-')# делит строку введённую на две части, чтоб потом поместить в словарь как начало и конец периода
       b_1 = str_popolam[0]# конец периода
       c_1 = str_popolam[1]# Рост или падение котировки в итоге
       d_1 = str_popolam[2]# Акция, в которую требуется добавить пример
    
    except FileNotFoundError:# Проверка на сущестование файла
        f = open('Days_14_example.json', 'w')
        f.close()
        if add_example() == 0:
            return 0
        else:
            return

    except:# Проверка на другие ощибки ввода
        print('ERROR SIMBOLS!!! Enter again...')
        if add_example() == 0:
            return 0
        else:
            return 
    
###########
    def razdelenie_in_part(b_1, df_1):# функция нужна для того чтоб выделить 14 дней от точки дня, которую мы задаём
        list_razdelen = b_1.split('/')
        num_1 = int(list_razdelen[0])
        num_2 = int(list_razdelen[1])
        num_3 = int(list_razdelen[2])

        for i in np.arange(0, 16, 1):# Отсчитывает 16 дней от конца до даты, которую надо опросить, выходные и праздники биржа не ведёт, поэтому стараемся приблизится к 14 дням сразу
            num_1 -= 1
            if num_1 == 0:
                num_1 = 31
                num_2 -= 1
                if num_2 == 0:
                    num_2 = 12
                    num_3 -= 1
        dni = 0
        while dni < 14:# цикл идёт пока не будет выявлено 14 дней по количеству ключей
            num_1_str = num_1
            num_2_str = num_2
            num_3_str = num_3
            if num_1 < 10:
                num_1_str = f'0{num_1}'
            if num_2 < 10:
                num_2_str = f'0{num_2}'
                num_3_str = str(num_3)
            a_1 = f'{num_1_str}/{num_2_str}/{num_3_str}'# составляется новый период
    
            sleep(5)# приостанавливает на 5 секунд, чтоб сервер не отрёкся от ip
            try:
                indi_1 = df_1.retrieve_historical_data(from_date=a_1, to_date=b_1).to_json()
                y_1 = json.loads(indi_1)
                print(len(y_1['Close'].keys()))
                dni = len(y_1['Close'].keys())# Проверяет сколько дней по ключам в отклике, должно быть 14

                num_1 -= 1
                if num_1 == 0:
                    num_1 = 31
                    num_2 -= 1
                    if num_2 == 0:
                        num_2 = 12
                        num_3 -= 1
                
            except ValueError:# если будет ошибка от запроса при передачи даты, скажем 31 дня не существует в этом месяце, то на день ментше станет
                num_1 -= 1
                if num_1 == 0:
                    num_1 = 31
                    num_2 -= 1
                    if num_2 == 0:
                        num_2 = 12
                        num_3 -= 1
            
        return a_1

########33
    o = json.load(f)
    try:# Проверка имя акции или id акции
        l = int(d_1)
    except ValueError:# Если было введёно имя, то оно сначала найдётся среди списка, найдёт его id, и пойдёт дальше
        Num = len(o['Example'].keys())
        for f in np.arange(0, Num, 1):
            try:# проверки на то есть в акции данные или только название есть
                nameik = list(o['Example'][str(f)].keys())
                if nameik[0] == d_1:
                    d_1 = str(f)
            except AttributeError:
                if o['Example'][str(f)] == d_1:
                    d_1 = str(f)
            except json.decoder.JSONDecodeError:
                if o['Example'][str(f)] == d_1:
                    d_1 = str(f)
        
    try:# Проврка на заполненность файла чем нибудь
        name_d_1s = list(o['Example'][d_1].keys())
        name_d_1 = name_d_1s[0]# проверка на заполненность ключа другими ключами, если есть ключ, значит у него есть своё значение
        Num = len(o['Example'][d_1][name_d_1].keys())# Считает сколько ключей в словаре именно в этой акции
        df_1 = inv.search_quotes(text=name_d_1, products=['stocks'], countries=['Russia'], n_results=1)
        a_1 = razdelenie_in_part(b_1, df_1)
        o['Example'][d_1][name_d_1].update({str(Num):{'from_date':a_1, 'to_date':b_1, 'Negative/Positive':c_1}})# Каждый раз при вызове он добавляет по ключу номер и период, начало и конец
    except json.decoder.JSONDecodeError:
        name_d_1 = o['Example'][d_1]# достаёт имя акции, если никаких данныз по акции в ней ещё нет
        df_1 = inv.search_quotes(text=name_d_1, products=['stocks'], countries=['Russia'], n_results=1)
        a_1 = razdelenie_in_part(b_1, df_1)# Возвращает период от которого будет начинаться срез данных
        o['Example'][d_1] = dict({name_d_1: {'0':{'from_date':a_1, 'to_date':b_1, 'Negative/Positive':c_1}}})# Заполняет сначала
    except AttributeError:
        name_d_1 = o['Example'][d_1]# достаёт имя акции, если никаких данныз по акции в неё ещё нет
        df_1 = inv.search_quotes(text=name_d_1, products=['stocks'], countries=['Russia'], n_results=1)
        a_1 = razdelenie_in_part(b_1, df_1)
        o['Example'][d_1] = dict({name_d_1: {'0':{'from_date':a_1, 'to_date':b_1, 'Negative/Positive':c_1}}})
    except:
        print('HELL ERROR!!!, Enter again...')
        if add_example() == 0:
            return 0
        else:
            return
    
    ######### Запрос данных по заданному периоду

    sleep(5)
    indi_1 = df_1.retrieve_historical_data(from_date=a_1, to_date=b_1).to_json()
    y_1 = json.loads(indi_1)
    it = 0
    Num = len(o['Example'][d_1][name_d_1].keys())
    for k in y_1['Close'].keys():
        C = y_1['Close'][k]
        V = y_1['Volume'][k]
        Ch = y_1['Change Pct'][k]
        Op = y_1['Open'][k]
        Hi = y_1['High'][k]
        L = y_1['Low'][k]

        try:
            o['Example'][d_1][name_d_1][str(Num-1)]['Data_14_days'].update({str(it): {'Close': C, 'Volume': V, 'Change Pct' : Ch, 'Open' : Op, 'High' : Hi, 'Low' : L}})
        except:
            o['Example'][d_1][name_d_1][str(Num-1)].update({'Data_14_days': {str(it): {'Close': C, 'Volume': V, 'Change Pct' : Ch, 'Open' : Op, 'High' : Hi, 'Low' : L}}})
        it += 1

    f = open('Days_14_example.json', 'w')# сохранение данных по периодам
    json.dump(o, f)
    f.close()

#################################################################добавлние новой акции

def add_new_stock():# добавляет название акции в список акций
    name_1 = input('Enter mini name stock, for example(sber): ')
    f = open('Days_14_example.json', 'r')
    jsn_1 = json.load(f)
    x = len(jsn_1['Example'].keys())
    jsn_1['Example'].update({str(x): name_1})# добавление записи об акции
    jsn_1['weight'].update({name_1: {"first layer": {"0": {"0": 0.5, "1": 0.4, "2": 0.3, "3": 0.5, "4": 0.5, "5": 0.5}, "1": {"0": 0.53, "1": 0.43, "2": 0.33, "3": 0.53, "4": 0.53, "5": 0.53}, "2": {"0": 0.55, "1": 0.45, "2": 0.35, "3": 0.55, "4": 0.55, "5": 0.55}, "3": {"0": 0.57, "1": 0.47, "2": 0.37, "3": 0.57, "4": 0.57, "5": 0.57}, "4": {"0": 0.6, "1": 0.5, "2": 0.4, "3": 0.6, "4": 0.6, "5": 0.6}, "5": {"0": 0.63, "1": 0.53, "2": 0.43, "3": 0.63, "4": 0.63, "5": 0.63}, "6": {"0": 0.65, "1": 0.55, "2": 0.45, "3": 0.65, "4": 0.65, "5": 0.65}, "7": {"0": 0.67, "1": 0.57, "2": 0.47, "3": 0.67, "4": 0.67, "5": 0.67}, "8": {"0": 0.7, "1": 0.6, "2": 0.5, "3": 0.7, "4": 0.7, "5": 0.7}, "9": {"0": 0.73, "1": 0.63, "2": 0.53, "3": 0.73, "4": 0.73, "5": 0.73}, "10": {"0": 0.75, "1": 0.65, "2": 0.55, "3": 0.75, "4": 0.75, "5": 0.75}, "11": {"0": 0.77, "1": 0.67, "2": 0.57, "3": 0.77, "4": 0.77, "5": 0.77}, "12": {"0": 0.8, "1": 0.7, "2": 0.6, "3": 0.8, "4": 0.8, "5": 0.8}, "13": {"0": 0.83, "1": 0.73, "2": 0.63, "3": 0.83, "4": 0.83, "5": 0.83}}, "second layer": {"0": 0.5, "1": 0.53, "2": 0.55, "3": 0.57, "4": 0.6, "5": 0.63, "6": 0.65, "7": 0.67, "8": 0.7, "9": 0.73, "10": 0.75, "11": 0.77, "12": 0.8, "13": 0.83}}})# Добавление начальных весов для конкретно этой акции
    f = open('Days_14_example.json', 'w')# сохранение данных по периодам
    json.dump(jsn_1, f)
    f.close()

################################################################# Удаление нескольких примеров из списка

def del_some_examples():# удаление нескольких периодов из списка
    show_list_examples()
    print('|__ INSTRUCTION __|: Write word "stop", to stop')
    stop_func = del_one_example()
    if stop_func == 0:
        return
    else:
        del_one_example()

################################################################# Удаление одного примера из списка

def del_one_example():# Удаляет один конкрентый пример из списка
    show_list_examples()
    try:# Проверка существования json файла
       f = open('Days_14_example.json', 'r')
       list_Days = json.load(f)
       try:# Проврека существования элемента в словаре
           ex2 = input('Delete "period-stock", for example (27-45) : ')
           if ex2 == 'stop':# Прерывет функцию при слове 'stop'
               return 0
           popolam_ex2 = ex2.split('-')

           j_num = list(list_Days['Example'][popolam_ex2[1]].keys())# наименование акции
           Ncount = str(len(list_Days['Example'][popolam_ex2[1]][j_num[0]].keys())-1)# Последний элемент в списке
           list_Days['Example'][popolam_ex2[1]][j_num[0]][popolam_ex2[0]] = list_Days['Example'][popolam_ex2[1]][j_num[0]][Ncount]# обмен значениями
           list_Days['Example'][popolam_ex2[1]][j_num[0]].pop(Ncount)
       except KeyError:
            print('ERROR KEY, Enter again...')
            if del_one_example() == 0:
                return 0
            else:
                return

       except:
            print('Unknown ERROR, Enter again...')
            if del_one_example() == 0:
                return 0
            else:
                return
    
    except FileNotFoundError:
        print('ERROR List, list not found!!! Need to add an example...')

    f = open('Days_14_example.json', 'w')
    json.dump(list_Days, f)
    f.close()

################################################################## Удаление всех примеров периодов из списка

def del_all_examples():# Удаляет все примеры
    ex = input('Are you sure you want to delete all examples? Yes - Y, No - N: ')
    if ex == 'N':# Прерывает функцию при слове 'stop'
           return 0
    f = open('Days_14_example.json', 'w')# файл стирается и записывается новый пустой
    f.close()

################################################## Показать список

def show_list_examples():# Показать список примеров
    try:
       f = open('Days_14_example.json', 'r')
       list_Days = json.load(f)
       f.close()
       way_1 = input('\nShow all examples of all stocks - 0 \nExamples one stock - 1 \nOnly list name stocks - 2\nEnter: ')
       if way_1 == '0':
           print('Id  ', 'Stock  ', 'Id', '            Period', '        Negative/Positive')
           v = len(list_Days['Example'].keys())# количество акций
           for o in np.arange(0, v, 1):
               try:
                   j_name = list(list_Days['Example'][str(o)].keys())# наименование акции
                   j_num = list(list_Days['Example'][str(o)][j_name[0]].keys())
                
                   for j in j_num:# Выводит список текущих примеров
                        print(o, '  ', j_name[0], '  ', j, '    ', list_Days['Example'][str(o)][j_name[0]][j]['from_date'], '-', list_Days['Example'][str(o)][j_name[0]][j]['to_date'], '      ',list_Days['Example'][str(o)][j_name[0]][j]['Negative/Positive'])
               except AttributeError:
                   j_name = list_Days['Example'][str(o)]
                   print(o, '  ',j_name, '     none periods')
               print('\n')
               
       elif way_1 == '1':
            Id_stock = input('Enter Id stock(25) or mini name stock(sber): ')

            ########

            try:# Проверка имя акции или id акции
                l = int(Id_stock)
            except ValueError:# Если было введёно имя, то оно сначала найдётся среди списка, найдёт его id, и пойдёт дальше
                Num = len(list_Days['Example'].keys())
                for f in np.arange(0, Num, 1):
                    try:# проверки на то есть в акции данные или только название есть
                        name_s = list(list_Days['Example'][str(f)].keys())
                        if name_s[0] == Id_stock:
                            Id_stock = str(f)
                    except AttributeError:
                        if list_Days['Example'][str(f)] == Id_stock:
                            Id_stock = str(f)
                    except json.decoder.JSONDecodeError:
                        if list_Days['Example'][str(f)] == Id_stock:
                            Id_stock = str(f)
            #######
            try:
                j_name = list(list_Days['Example'][Id_stock].keys())# наименование акции
                print('Id  ', 'Stock   ', 'Id', '           Period', '        Negative/Positive')
                for i in list(list_Days['Example'][Id_stock][j_name[0]].keys()):# Выводит список текущих примеров одной акции
                    print(Id_stock, '  ', j_name[0], '  ', i, '    ', list_Days['Example'][Id_stock][j_name[0]][i]['from_date'], '-', list_Days['Example'][Id_stock][j_name[0]][i]['to_date'], '      ',list_Days['Example'][Id_stock][j_name[0]][i]['Negative/Positive'])
            except AttributeError:# Проверка на заполненность акции чем нибудь
                   j_name = list_Days['Example'][Id_stock]
                   print(o, '  ',j_name, '     none periods')
            print('\n')

       elif way_1 == '2':
           v = len(list_Days['Example'].keys())
           print('Id  Name')
           for o in np.arange(0, v, 1):
               try:
                   j_name = list(list_Days['Example'][str(o)].keys())
                   print(o, ' ', j_name[0])
               except AttributeError:# поверка следит за тем заполена ли акция вообще хоть чем то
                   print(o, ' ', list_Days['Example'][str(o)])
       elif way_1 == '3':
           name_stock = input('Enter mini name stock, for example(sber): ')
           v = len(list_Days['Example'].keys())
           print('\nId  Name')
           s = False
           for o in np.arange(0, v, 1):
               try:
                   j_name = list(list_Days['Example'][str(o)].keys())
                   j_name = j_name[0]
               except AttributeError:
                   j_name = list_Days['Example'][str(o)]
               if name_stock == j_name:
                   print(o, ' ', j_name)
                   print('\nStock is there in list\n')
                   s = True
                   break
           if s == False:
                print('\nStock is not there in list...\n')

    except:
        print('\n', 'No List!!! need to add...')

    

######################################
###################################### Сигнал от индикатора по нахождению графика ниже 30%

def proverkaRSI():
    import datetime
    f = open('Days_14_example.json', 'r')
    jsn_2 = json.load(f)
    f.close()
    v = len(jsn_2['Example'].keys())# количество ключей названий акций
    global exit_radius
    while exit_radius != True:# циклическая через время для мониторинга
        right_road = False
        while right_road != True:# проверяет период времени когда биржа активна и только в него рабоатет
            h = datetime.datetime.today()
            if h.hour == 11 and h.minute >= 40:
                right_road = True
            elif h.hour > 11:
                right_road = True
            elif h.hour < 1:
                right_road = True
            elif h.hour == 1 and h.minute <= 40:
                right_road = True
            else:
                sleep(600)
        for i in np.arange(0, v, 1):# Цикл проходится по всем ключам
            if exit_radius == True:# ВЫход из программы
                return
            try:
                name_stock = list(jsn_2['Example'][str(i)].keys())# достаёт наименовние акции
            except AttributeError:
                continue
            df_1 = inv.search_quotes(text=name_stock[0], products=['stocks'], countries=['Russia'], n_results=1)
            indi = df_1.retrieve_technical_indicators(interval='daily').to_json()
            y = json.loads(indi)
            print('Stock border RSI: ', name_stock[0], ' = ', y['value']['0'], '%')# Проверка процента RSI
            if y['value']['0'] < 30:# проверяет в какой зоне график по индикатору RSI            
                sleep(5)
                try:
                   progress_network = main_real_birzha(df_1, name_stock[0])
                   if progress_network >= 0.9:
                       birzha_notification(name_stock[0], progress_network)
                       print(f'GOOD SIGNAL, /_ Probability : ', round(progress_network*100, 5),' % _/\n')
                   else:
                       print('Signal while low, /_ Probability : ', round(progress_network*100, 5),' % _/\n')
                except IndexError:# ошибка запроса к акции, если не торгуется...
                    continue
            sleep(5)
        print('\n\nPlease wait 20 minutes before repeating the monitoring!!!')
        sleep(1200)# ожидание каждые 20 минут на то, чтоб проверить потом ещё раз и ещё раз

###################################### уменьшения данных для нейронной сети

def decrease_data(num):
    del_num = 0
    if 100000000000 < num <= 1000000000000 or -100000000000 >= num > -1000000000000:
        del_num = 1000000000000
    elif 10000000000 < num <= 100000000000 or -10000000000 >= num > -100000000000:
        del_num = 100000000000
    elif 1000000000 < num <= 10000000000 or -1000000000 >= num > -10000000000:
        del_num = 10000000000
    elif 100000000 < num <= 1000000000 or -100000000 >= num > -1000000000:
        del_num = 1000000000
    elif 10000000 < num <= 100000000 or -10000000 >= num > -100000000:
        del_num = 100000000
    elif 1000000 < num <= 10000000 or -1000000 >= num > -10000000:
        del_num = 10000000
    elif 100000 < num <= 1000000 or -100000 >= num > -1000000:
        del_num = 1000000
    elif 10000 < num <= 100000 or -10000 >= num > -100000:
        del_num = 100000
    elif 1000 < num <= 10000 or -1000 >= num > -10000:
        del_num = 10000
    elif 100 < num <= 1000 or -100 >= num > -1000:
        del_num = 1000
    elif 10 < num <= 100 or -10 >= num > -100:
        del_num = 100
    elif 1 < num <= 10 or -1 >= num > -10:
        del_num = 10
    elif 0 < num <= 1 or 0 >= num > -1:
        del_num = 1
    
    return del_num# Делитель

####################################### Функция активации Сигмоида

def Sigmoida(x): #функция активации для нейрона, сигмоида, получившиеся значение будет в диапазоне [0, 1]
    print('Переданный x: ', x)
    hr = 1/(1+(1/np.exp(x)))
    #print('Результат работы нейрона: ', hr, '\n==================================')
    return hr

################################################ Онлайн данные по котировке

def main_real_birzha(df_1, name_stock):# Функция по реальному времени анализирующая котировку
    indi_1 = df_1.retrieve_recent_data().to_json()# запршиваются данные за последние дни, недели
    y_1 = json.loads(indi_1)
    proba = list(y_1['Close'].keys())# смотрит все ключи(индексы) и записывает их в лист, чтоб потом достать определённеы дни и данные
    reverse14List = []
    for i in np.arange(0, 14, 1):
        proba[-1-i]
        reverse14List.append(proba[-1-i])# нужно чтоб лишь 14 дней из всего списка обрезалось
    reverse14List.reverse()# Переворот списка

    W_mas = np.zeros((14, 6))# создание массива заполненного нулями
    W_mas_H = np.zeros(14)# создание массива заполненного нулями
    Data_Days = np.zeros((14, 6))
    iter = 0
    num1 = 0
    num2 = 0
    num3 = 0
    num4 = 0
    num5 = 0
    num6 = 0

    for i in reverse14List:# обходит данные каждого дня в пределах 14 дней
        Data_Days[iter][0] = y_1['Close'][i]
        if np.absolute(Data_Days[iter][0]) > num1:
            num1 = Data_Days[iter][0]# проверка для нахождения самого большого числа в списке
        Data_Days[iter][1] = y_1['Volume'][i]
        if np.absolute(Data_Days[iter][1]) > num2:
            num2 = Data_Days[iter][1]
        Data_Days[iter][2] = y_1['Change Pct'][i]
        if np.absolute(Data_Days[iter][2]) > num3:
            num3 = Data_Days[iter][2]
        Data_Days[iter][3] = y_1['Open'][i]
        if np.absolute(Data_Days[iter][3]) > num4:
            num4 = Data_Days[iter][3]
        Data_Days[iter][4] = y_1['High'][i]
        if np.absolute(Data_Days[iter][4]) > num5:
            num5 = Data_Days[iter][4]
        Data_Days[iter][5] = y_1['Low'][i]
        if np.absolute(Data_Days[iter][5]) > num6:
            num6 = Data_Days[iter][5]
        iter += 1
    
    del_data1 = decrease_data(num1)# находится через функцию общий делитель для каждого типа данных
    del_data2 = decrease_data(num2)
    del_data3 = decrease_data(num3)
    del_data4 = decrease_data(num4)
    del_data5 = decrease_data(num5)
    del_data6 = decrease_data(num6)

    for n in np.arange(0, 14, 1):# Делится для уменьшения значения
        Data_Days[n][0] = Data_Days[n][0]/del_data1
        Data_Days[n][1] = Data_Days[n][1]/del_data2
        Data_Days[n][2] = Data_Days[n][2]/del_data3
        Data_Days[n][3] = Data_Days[n][3]/del_data4
        Data_Days[n][4] = Data_Days[n][4]/del_data5
        Data_Days[n][5] = Data_Days[n][5]/del_data6

    f = open('Days_14_example.json', 'r')
    data_jsn = json.load(f)
    for i in np.arange(0, 14, 1):# Заполнение массивов значениями из json файла
        W_mas[i][0] = data_jsn['weight'][name_stock]['first layer'][str(i)]['0']
        W_mas[i][1] = data_jsn['weight'][name_stock]['first layer'][str(i)]['1']
        W_mas[i][2] = data_jsn['weight'][name_stock]['first layer'][str(i)]['2']
        W_mas[i][3] = data_jsn['weight'][name_stock]['first layer'][str(i)]['3']
        W_mas[i][4] = data_jsn['weight'][name_stock]['first layer'][str(i)]['4']
        W_mas[i][5] = data_jsn['weight'][name_stock]['first layer'][str(i)]['5']

        W_mas_H[i] = data_jsn['weight'][name_stock]['second layer'][str(i)]
    Weightss = [W_mas, W_mas_H]# Компановка для лучше передачи

    list_result_for_weight = main_neyron_network(Weightss, Data_Days)
    #print('\n/_ Probability : ', round(list_result_for_weight[0]*100, 3), '% _/')
    
    return list_result_for_weight[0]

################################################################# Нейронная сеть

def main_neyron_network(Weghtss, Data_Days):
    W_mas = Weghtss[0]
    W_mas_H = Weghtss[1]
    b = 0# пока просто неиспользуемый шаг в нейронке
    H_mas = np.zeros(14)# Список первых данных после функции активации, но тут пока 14 нулей

    for iter in np.arange(0, 14, 1):# обходит данные каждого дня
        H_mas[iter] = Sigmoida(Data_Days[iter][0]*W_mas[iter][0] + Data_Days[iter][1]*W_mas[iter][1] + Data_Days[iter][2]*W_mas[iter][2] + Data_Days[iter][3]*W_mas[iter][3] + Data_Days[iter][4]*W_mas[iter][4] + Data_Days[iter][5]*W_mas[iter][5] + b)# добавление в список первых значений после сигмоиды

    #print(W_mas)
    #print('Результат нейронов первого слоя: ', H_mas)

############ Расчёт второго слоя

    res = 0
    for i in np.arange(0, 14, 1):
        res += H_mas[i]*W_mas_H[i]
    H_mas_result = Sigmoida(res + b)# Результат слоя + b шаг

    #print('Результат нейрона второго слоя: ', H_mas_result)# Проверка
    list_result_for_weight = [H_mas_result, H_mas, W_mas, W_mas_H, Data_Days]# список выводимых параметров
    
    return list_result_for_weight

################################################ Корректировка Весов 

def weight_correction(y, list_result_for_weight):
    H_mas_result = list_result_for_weight[0]# Всё что можно было взять из нейрона
    #print(H_mas_result)
    H_mas = list_result_for_weight[1]
    W_mas = list_result_for_weight[2]
    W_mas_H = list_result_for_weight[3]
    Data_Days = list_result_for_weight[4]

    e = H_mas_result - y # отклонение от того, что должно получиться
    lambdaa = 0.1 #шаг сходимости


    for it in np.arange(0, 14, 1):# Иттерация по каждому дню
        W_mas_H[it] = W_mas_H[it] - (lambdaa*e*H_mas_result*(1-H_mas_result)*H_mas[it])#пересчёт веса первого слоя
        # Далее каждый вес от каждого дня по первому слою так как там три типа данных то и три пересчёта веса
        #print('lambda ', lambdaa, '\n e: ', e, '\n H_mas_result: ', H_mas_result, '\n W_mas_H: ', W_mas_H[it], '\n H_mas: ', H_mas, '\n Data_Days: ', Data_Days[it][0])
    
        W_mas[it][0] = W_mas[it][0] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][0])
        W_mas[it][1] = W_mas[it][1] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][1])
        W_mas[it][2] = W_mas[it][2] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][2])
        W_mas[it][3] = W_mas[it][3] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][3])
        W_mas[it][4] = W_mas[it][4] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][4])
        W_mas[it][5] = W_mas[it][5] - (lambdaa*e*H_mas_result*(1-H_mas_result)*W_mas_H[it]*H_mas[it]*(1-H_mas[it])*Data_Days[it][5])
        
        
    H_mas = 0# очистка результата слоёв для следующей тренировки
    H_mas_result = 0

    #print('Текущие веса первого слоя: ', W_mas)
    #print('Текущие веса второго слоя: ', W_mas_H)
    #print('Разброс ошибки: ', e)

    Weightss = [W_mas, W_mas_H, e]# e тут требуется, чтоб передать в лог операций, если он вообще будет нужен

    return Weightss

################################################################# Фунция управления тренировачной нейронной сетью

def neural_network_manager():
    from progress.bar import IncrementalBar
    W_mas = np.zeros((14, 6))# создание массива заполненного нулями
    W_mas_H = np.zeros(14)# создание массива заполненного нулями
    f = open('Days_14_example.json', 'r')
    data_jsn = json.load(f)
    enter_1 = input('\nTraining all stocks - 0\nTraining one stock - 1\nEnter: ')

    if enter_1 == '0':# Выбор тренировки одной конкретной акции или всех
        inp = input('\nHow many training cycles do you need? For example(3)\nEnter: ')
        xter = len(data_jsn['Example'].keys())# считает количество акций
        t = 0
    elif enter_1 == '1':
        inp = input('\nHow many training cycles do you need? For example(3)\nEnter: ')
        name_t = input('\nEnter mini name stock.. For example (sber)\nEnter: ')
        xter = len(data_jsn['Example'].keys())
        for s in np.arange(0, xter, 1):
            try:# проверка на заполенность и существовании данных акции
                name_s = list(data_jsn['Example'][str(s)].keys())
            except AttributeError:
                continue
            if name_s[0] == name_t:
                t = s
                xter = t + 1
                break
    else:
        return
    bar = IncrementalBar('Progress: ', max=int(inp))
    list_LOG = []
    import time
    import datetime
    for w in np.arange(0, int(inp), 1):# Задаёт количество иттераций для тренировки
        hrono_tochka = time.time()# точка отсчёта хранится для определеия сколько времени займёт тренировка
        for j in np.arange(t, xter, 1):#  пробегается по акциям
            try:
                j_num_t = list(data_jsn['Example'][str(j)].keys())# наименование акции
                j_num = j_num_t[0]
            except AttributeError:
                continue# продолжает, если вдруг в акции нет примеров
            #######
            
            for i in np.arange(0, 14, 1):# Заполнение массивов значениями из json файла
                W_mas[i][0] = data_jsn['weight'][j_num]['first layer'][str(i)]['0']
                W_mas[i][1] = data_jsn['weight'][j_num]['first layer'][str(i)]['1']
                W_mas[i][2] = data_jsn['weight'][j_num]['first layer'][str(i)]['2']
                W_mas[i][3] = data_jsn['weight'][j_num]['first layer'][str(i)]['3']
                W_mas[i][4] = data_jsn['weight'][j_num]['first layer'][str(i)]['4']
                W_mas[i][5] = data_jsn['weight'][j_num]['first layer'][str(i)]['5']

                W_mas_H[i] = data_jsn['weight'][j_num]['second layer'][str(i)]
    
            Weightss = [W_mas, W_mas_H]
            
            if w == (int(inp)-1):
                list_LOG.append('\n###### NAME STOCK ######')
                list_LOG.append(j_num)# в список ЛОГа добавляется "имя акции"
            #######
            x = len(data_jsn['Example'][str(j)][j_num].keys())# считает количество примеров в акции
            for k in np.arange(0, x, 1): #!!!! x !!!! количество примеров, надо пройти по всем до 'x' не включая 'x'         
                num1 = 0
                num2 = 0
                num3 = 0
                num4 = 0
                num5 = 0
                num6 = 0
                Data_Days = np.zeros((14, 6))
                for n in np.arange(0, 14, 1):# данные от примеров сохранённых в json файле
                    Data_Days[n][0] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['Close']
                    if np.absolute(Data_Days[n][0]) > num1:
                        num1 = Data_Days[n][0]# проверка для нахождения самого большого числа в списке
                    Data_Days[n][1] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['Volume']
                    if np.absolute(Data_Days[n][1]) > num2:
                        num2 = Data_Days[n][1]
                    Data_Days[n][2] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['Change Pct']
                    if np.absolute(Data_Days[n][2]) > num3:
                        num3 = Data_Days[n][2]
                    Data_Days[n][3] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['Open']
                    if np.absolute(Data_Days[n][3]) > num4:
                        num4 = Data_Days[n][3]
                    Data_Days[n][4] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['High']
                    if np.absolute(Data_Days[n][4]) > num5:
                        num5 = Data_Days[n][4]
                    Data_Days[n][5] = data_jsn['Example'][str(j)][j_num][str(k)]['Data_14_days'][str(n)]['Low']
                    if np.absolute(Data_Days[n][5]) > num6:
                        num6 = Data_Days[n][5]
            
                del_data1 = decrease_data(num1)# находится через функцию общий делитель для каждого типа данных
                del_data2 = decrease_data(num2)
                del_data3 = decrease_data(num3)
                del_data4 = decrease_data(num4)
                del_data5 = decrease_data(num5)
                del_data6 = decrease_data(num6)

                for n in np.arange(0, 14, 1):# Делится для уменьшения значения
                    Data_Days[n][0] = Data_Days[n][0]/del_data1
                    Data_Days[n][1] = Data_Days[n][1]/del_data2
                    Data_Days[n][2] = Data_Days[n][2]/del_data3
                    Data_Days[n][3] = Data_Days[n][3]/del_data4
                    Data_Days[n][4] = Data_Days[n][4]/del_data5
                    Data_Days[n][5] = Data_Days[n][5]/del_data6

                res = main_neyron_network(Weightss, Data_Days)# Вызывает главную тренировачную сеть и передаёт в неё массивом весов хранившиеся в json файле
                y = int(data_jsn['Example'][str(j)][j_num][str(k)]['Negative/Positive'])
                Weightss = weight_correction(y, res)# корректировка весов
                
                if w == (int(inp)-1):
                    if k >= (x-4):
                        list_LOG.append(Weightss[2])# в список ЛОГа добавляется "е", требуется для лога событий 5 значений, если нужно
            ###### Перевод в json файл то что по весам нашлось
            W_mas = Weightss[0]
            W_mas_H = Weightss[1]
            for b in np.arange(0, 14, 1):
                data_jsn['weight'][j_num]['first layer'][str(b)]['0'] = W_mas[b][0]
                data_jsn['weight'][j_num]['first layer'][str(b)]['1'] = W_mas[b][1]
                data_jsn['weight'][j_num]['first layer'][str(b)]['2'] = W_mas[b][2]
                data_jsn['weight'][j_num]['first layer'][str(b)]['3'] = W_mas[b][3]
                data_jsn['weight'][j_num]['first layer'][str(b)]['4'] = W_mas[b][4]
                data_jsn['weight'][j_num]['first layer'][str(b)]['5'] = W_mas[b][5]

                data_jsn['weight'][j_num]['second layer'][str(b)] = W_mas_H[b]
        bar.next()
        hrono_iter = time.time() - hrono_tochka# одна иттерация заняла столько времени
        if w == 0:
            hrono_tik = hrono_iter + (hrono_iter * int(inp))# общее время иттераций
        hrono_tik = hrono_tik - hrono_iter# каждую иттерациб время из общего будет вычитаться прошедшее
        if hrono_tik <= 0:
            print('  Time complete: 00:00:00...')
        else:
            hronometr = datetime.timedelta(seconds=hrono_tik)
            print('  Time complete: ', hronometr)
    bar.finish()
    f = open('Days_14_example.json', 'w')
    json.dump(data_jsn, f)
    f.close()
    entr_2 = input('Do you need LOG last five operations all stocks? y/n: ')
    if entr_2 == 'y':
        for h in list_LOG:
            print(h)

################################################
def animahron():# нужен для того чтоб параллельно считать время бездействия
    sleep(15)
    global orn_1
    orn_1 = True
    return orn_1
################################################

exit_radius = False
hron = Thread(target=animahron)# поток для времени чтоб распараллелить процессы
hron.start()
orn = False
orn_1 = False
print('|__ INSTRUCTION __|\nIf you need a menu, then press the button "ESC" for 1 minute\n')
while orn_1 != True:
    if keyb.is_pressed('esc'):
        orn = True
        main()
if orn == False:
    proverkaRSI()
    main()