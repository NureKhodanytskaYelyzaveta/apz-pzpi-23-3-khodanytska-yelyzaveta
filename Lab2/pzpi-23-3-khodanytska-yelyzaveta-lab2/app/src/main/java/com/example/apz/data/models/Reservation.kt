package com.example.apz.data.models

data class CreateReservationRequest(
    val user_id: Int,
    val book_id: Int
)

data class ReservationResponse(
    val reservation_id: Int,
    val book_id: Int,
    val expiry_date: String
)

data class CancelReservationResponse(
    val reservation_id: Int,
    val status: String,
    val message: String
)

