package com.example.apz.data.api

import com.example.apz.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface LibraryApi {

    // Auth
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    // Books
    @GET("books/search")
    suspend fun searchBooks(@Query("q") query: String): List<BookResponse>

    // User
    @GET("users/{user_id}")
    suspend fun getUser(@Path("user_id") userId: Int): Response<UserProfile>

    // Loans
    @GET("users/{user_id}/loans/active")
    suspend fun getActiveLoans(@Path("user_id") userId: Int): List<ActiveLoanResponse>

    @GET("users/{user_id}/loans")
    suspend fun getLoanHistory(@Path("user_id") userId: Int): List<LoanHistoryResponse>

    @POST("loans/{loan_id}/extend")
    suspend fun extendLoan(
        @Path("loan_id") loanId: Int,
        @Body request: ExtendLoanRequest
    ): Response<ExtendLoanResponse>

    // Reservations
    @POST("reservations/")
    suspend fun createReservation(
        @Body request: CreateReservationRequest
    ): Response<ReservationResponse>

    @POST("reservations/{reservation_id}/cancel")
    suspend fun cancelReservation(
        @Path("reservation_id") reservationId: Int
    ): Response<CancelReservationResponse>

    // Додай цей метод у інтерфейс:
    @GET("users/{user_id}/reservations/active")
    suspend fun getActiveReservations(@Path("user_id") userId: Int): List<ReservationResponse>
}