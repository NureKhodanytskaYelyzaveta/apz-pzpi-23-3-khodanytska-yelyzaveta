package com.example.apz.utils

object Constants {
    // Для емулятора Android використовуємо 10.0.2.2 замість localhost
    // Якщо сервер на іншому комп'ютері - заміни на його IP-адресу
    const val BASE_URL = "http://10.0.2.2:5000/"

    const val USER_ID_KEY = "user_id"
    const val USER_NAME_KEY = "user_name"
    const val USER_EMAIL_KEY = "user_email"
    const val USER_ROLE_KEY = "user_role"
}