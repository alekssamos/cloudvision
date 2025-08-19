# -*- coding: utf-8 -*-
# CloudVision
# Author: ilyapashuk
# Copyright 2025, released under GPL.

import json
import base64
from logHandler import log
from .advanced_http_pool import AdvancedHttpPool
from .cvhelpers import get_image_content_from_image
from .cvconf import getConfig
from .cvexceptions import APIError


class MathpixError(APIError):
    """Исключение, возникающее при ошибках в работе с Mathpix API"""

    pass


def mathpixOCR(image: any, lang: str = "en"):
    """
    Распознает математические формулы на изображении с помощью Mathpix API.

    Args:
        image: Изображение в виде файла, URL или бинарных данных
        lang: Язык распознавания (не используется в Mathpix, но нужен для совместимости)

    Returns:
        Строка с распознанным текстом в формате mathpix-markdown
    """
    image_content = get_image_content_from_image(image)
    if not image_content:
        raise MathpixError("Не удалось получить содержимое изображения")

    # Кодируем изображение в base64
    img_base64 = base64.b64encode(image_content).decode("ascii")
    img_data = "data:image/png;base64," + img_base64

    # Параметры запроса к API - используем только формат "text"
    params = {"src": img_data, "formats": ["text"]}

    # Получаем API-ключ из настроек
    api_key = getConfig()["mathpixAPIKey"]
    if not api_key:
        raise MathpixError("API-ключ Mathpix не указан в настройках")

    # Формируем заголовки запроса
    headers = {
        "app_id": "nvda_cloudvision",
        "app_key": api_key,
        "Content-Type": "application/json",
    }

    # Отправляем запрос к API
    http = AdvancedHttpPool().Pool
    try:
        response = http.request(
            "POST", "https://api.mathpix.com/v3/text", headers=headers, json=params
        )
        result = response.json()
    except Exception as e:
        log.error(f"Ошибка при запросе к Mathpix API: {e}")
        raise MathpixError(f"Ошибка при запросе к Mathpix API: {e}")

    # Проверяем наличие ошибок в ответе
    if "error" in result:
        log.error(f"Ошибка Mathpix API: {result['error']}")
        raise MathpixError(f"Ошибка Mathpix API: {result['error']}")

    # Возвращаем результат в формате mathpix-markdown
    return result.get("text", "")
