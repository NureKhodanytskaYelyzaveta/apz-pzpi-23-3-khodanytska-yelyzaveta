package com.example.apz.presentation.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.apz.data.models.ReservationResponse
import com.example.apz.data.repository.LibraryRepository
import com.example.apz.utils.DataStoreHelper
import com.example.apz.utils.Result
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ReservationViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = LibraryRepository(application)

    private val _reservations = MutableStateFlow<List<ReservationResponse>>(emptyList())
    val reservations: StateFlow<List<ReservationResponse>> = _reservations.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    fun loadActiveReservations() {
        viewModelScope.launch {
            _isLoading.value = true
            val userId = DataStoreHelper.getUserId(getApplication())

            if (userId != null) {
                val result = repository.getActiveReservations(userId)

                when (result) {
                    is Result.Success -> {
                        _reservations.value = result.data
                        println("✅ Завантажено бронювань: ${result.data.size}")
                    }
                    is Result.Error -> {
                        _message.value = "Помилка: ${result.message}"
                        println("❌ Помилка завантаження: ${result.message}")
                    }
                    Result.Loading -> Unit
                }
            }
            _isLoading.value = false
        }
    }

    fun reserveBook(bookId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _message.value = null

            val result = repository.createReservation(bookId)

            when (result) {
                is Result.Success -> {
                    _message.value = "Книгу успішно заброньовано!"
                    loadActiveReservations() // ✅ Оновлюємо після бронювання
                }
                is Result.Error -> {
                    _message.value = "Помилка: ${result.message}"
                }
                Result.Loading -> Unit
            }
            _isLoading.value = false
        }
    }

    fun cancelReservation(reservationId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _message.value = null

            println("🔄 Скасування бронювання ID: $reservationId")
            val result = repository.cancelReservation(reservationId)

            when (result) {
                is Result.Success -> {
                    println("✅ Бронювання скасовано успішно")
                    _message.value = "Бронювання скасовано"
                    loadActiveReservations() // ✅ НАЙГОЛОВНІШЕ - оновлюємо список!
                }
                is Result.Error -> {
                    println("❌ Помилка скасування: ${result.message}")
                    // Якщо бронювання вже скасоване, все одно оновлюємо список
                    if (result.message.contains("вже скасовано", ignoreCase = true) ||
                        result.message.contains("not found", ignoreCase = true)) {
                        loadActiveReservations()
                    } else {
                        _message.value = "Помилка: ${result.message}"
                    }
                }
                Result.Loading -> Unit
            }
            _isLoading.value = false
        }
    }

    fun clearMessage() {
        _message.value = null
    }
}