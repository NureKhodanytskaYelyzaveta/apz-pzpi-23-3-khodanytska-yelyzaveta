package com.example.apz.data.models

data class ActiveLoanResponse(
    val loan_id: Int,
    val book_title: String,
    val due_date: String
)

data class LoanHistoryResponse(
    val loan_id: Int,
    val book_title: String,
    val due_date: String,
    val return_date: String?
)

data class ExtendLoanRequest(
    val days: Int = 7
)

data class ExtendLoanResponse(
    val loan_id: Int,
    val new_due_date: String
)