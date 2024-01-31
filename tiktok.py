import telegram
from time import sleep
from TikTokApi import TikTokApi
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

def write_last_time(t):
    try:
        logging.info('Обновление файла с последним временем')
        with open('last_time.txt', 'w') as f:
            f.write(str(t))
    except Exception as e:
        logging.error(str(e))

def read_last_time():
    logging.info('Чтение файла с последним временем')
    with open('last_time.txt', 'r') as f:
        pre_time = int(f.read())
    return pre_time

def save_video(video_bytes):
    logging.info('Сохранение видео')
    with open("video.mp4", "wb") as out:
        out.write(video_bytes)

def send_message():
    logging.info('Отправка сообщения в Telegram')
    try:   
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_video(chat_id='-1001257681765', video=open('video.mp4', 'rb'), supports_streaming=True)
        # Замените chat_id на id вашего телеграм-канала
    except Exception as e:
        print('Ошибка отправки сообщения в Telegram')
        logging.error('Ошибка отправки сообщения в Telegram')
        logging.error(str(e))

def within_running_hours():
    now = datetime.now().time() 
    start = datetime.strptime("00:00:00", "%H:%M:%S").time()
    end = datetime.strptime("23:59:00", "%H:%M:%S").time()

    # Check if the current time is within running hours
    return start <= now <= end


logging.info('Начало выполнения')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_API_KEY')

verifyfp = 'verify_9cedeca1f88dbe1ee89b08524dc764ef'
logging.info('Создание экземпляра API')
last_api_req = 'Создание'
sleep(5)
#api = TikTokApi.get_instance()
api = TikTokApi.get_instance(proxy="159.197.128.163:3128")

logging.info('Генерация идентификатора устройства')
sleep(5)
last_api_req = 'Генерация'
device_id = api.generate_device_id()

count = 1

while True:
    try:
        if within_running_hours():
            pre_time = read_last_time()
            tiktoks = ''

            logging.info('Получение тиктоков пользователя')
            last_api_req = 'Пользователь'
            tiktoks = api.by_username("webtoon_joy", count=count, custom_verifyFp=verifyfp, use_test_endpoints=True)

            for tiktok in tiktoks:
                if tiktok['createTime'] != pre_time:
                    logging.info('Новое видео, получаем данные видео')
                    sleep(5)
                    last_api_req = 'Видео'
                    video_bytes = api.get_video_by_tiktok(tiktok, custom_device_id=device_id, custom_verifyFp=verifyfp)

                    save_video(video_bytes)             
                    send_message()
                    write_last_time(tiktok['createTime'])
                else:
                    logging.info('Нет нового видео')
        else:
            logging.info('Вне рабочего времени')
            # Дополнительное ожидание 25 минут вне рабочего времени
            sleep(1500)

        sleep(350)

    except KeyboardInterrupt:
        logging.info('Прерывание с клавиатуры')
        break
    except Exception as e:
        logging.error('Общее исключение')
        logging.info(str(e))
        logging.info(last_api_req)
        sleep(350)
        continue
