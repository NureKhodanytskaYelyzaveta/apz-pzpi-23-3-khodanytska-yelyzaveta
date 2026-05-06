package com.example.apz.data.models

data class BookResponse(
    val book_id: Int,
    val title: String,
    val author: String,
    val status: String
)

data class BookDetail(
    val book_id: Int,
    val title: String,
    val author: String,
    val category: String?,
    val isbn: String?,
    val condition: String?,
    val status: String,
    val location: String?,
    val tags: String?
)