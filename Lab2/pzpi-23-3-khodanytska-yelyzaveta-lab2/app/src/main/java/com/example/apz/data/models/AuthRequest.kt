package com.example.apz.data.models

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    val user_id: Int,
    val name: String,
    val email: String,
    val role: String
)