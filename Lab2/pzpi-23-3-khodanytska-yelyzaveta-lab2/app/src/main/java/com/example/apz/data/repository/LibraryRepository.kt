package com.example.apz.data.repository

import android.content.Context
import com.example.apz.data.api.RetrofitClient
import com.example.apz.data.models.*
import com.example.apz.utils.DataStoreHelper
import com.example.apz.utils.Result

class LibraryRepository(private val context: Context) {

    private val api = RetrofitClient.api

    suspend fun login(email: String, password: String): Result<LoginResponse> = try {
        val response = api.login(LoginRequest(email, password))
        if (response.isSuccessful && response.body() != null) {
            val user = response.body()!!
            DataStoreHelper.saveUserSession(context, user.user_id, user.name, user.email, user.role)
            Result.Success(user)
        } else {
            Result.Error("Помилка входу: ${response.code()}")
        }
    } catch (e: Exception) {
        Result.Error(e.localizedMessage ?: "Невідома помилка мережі")
    }

    suspend fun searchBooks(query: String): Result<List<BookResponse>> = try {
        Result.Success(api.searchBooks(query))
    } catch (e: Exception) {
        Result.Error(e.localizedMessage ?: "Помилка пошуку")
    }

    suspend fun getActiveLoans(): Result<List<ActiveLoanResponse>> {
        val userId = DataStoreHelper.getUserId(context) ?: return Result.Error("Користувач не авторизований")
        return try {
            Result.Success(api.getActiveLoans(userId))
        } catch (e: Exception) {
            Result.Error(e.localizedMessage ?: "Помилка завантаження позик")
        }
    }

    suspend fun extendLoan(loanId: Int, days: Int): Result<ExtendLoanResponse> = try {
        val response = api.extendLoan(loanId, ExtendLoanRequest(days))
        if (response.isSuccessful && response.body() != null) {
            Result.Success(response.body()!!)
        } else {
            Result.Error("Помилка продовження: ${response.code()}")
        }
    } catch (e: Exception) {
        Result.Error(e.localizedMessage ?: "Помилка мережі")
    }

    suspend fun createReservation(bookId: Int): Result<ReservationResponse> {
        val userId = DataStoreHelper.getUserId(context) ?: return Result.Error("Користувач не авторизований")
        return try {
            val response = api.createReservation(CreateReservationRequest(userId, bookId))
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Error("Помилка бронювання: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.localizedMessage ?: "Помилка мережі")
        }
    }

    suspend fun logout() {
        DataStoreHelper.clearSession(context)
    }

    // Додай цей метод у клас:
    suspend fun getActiveReservations(userId: Int): Result<List<ReservationResponse>> {
        return try {
            val response = api.getActiveReservations(userId)
            Result.Success(response)
        } catch (e: Exception) {
            Result.Error(e.localizedMessage ?: "Помилка завантаження бронювань")
        }
    }

    suspend fun cancelReservation(reservationId: Int): Result<CancelReservationResponse> {
        return try {
            val response = api.cancelReservation(reservationId)
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Error("Помилка скасування: ${response.code()}")
            }
        } catch (e: Exception) {
            Result.Error(e.localizedMessage ?: "Помилка мережі")
        }
    }
}