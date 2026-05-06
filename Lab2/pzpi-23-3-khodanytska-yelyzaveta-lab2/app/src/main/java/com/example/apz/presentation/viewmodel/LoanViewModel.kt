package com.example.apz.presentation.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.apz.data.models.ActiveLoanResponse
import com.example.apz.data.repository.LibraryRepository
import com.example.apz.utils.Result
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class LoanViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = LibraryRepository(application)

    private val _loans = MutableStateFlow<List<ActiveLoanResponse>>(emptyList())
    val loans: StateFlow<List<ActiveLoanResponse>> = _loans.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _message = MutableStateFlow<String?>(null)
    val message: StateFlow<String?> = _message.asStateFlow()

    fun loadActiveLoans() {
        viewModelScope.launch {
            _isLoading.value = true
            val result = repository.getActiveLoans()

            if (result is Result.Success) {
                _loans.value = result.data
            } else if (result is Result.Error) {
                _message.value = result.message
            }
            _isLoading.value = false
        }
    }

    fun extendLoan(loanId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = repository.extendLoan(loanId, days = 7)

            if (result is Result.Success) {
                _message.value = "Позику продовжено до ${result.data.new_due_date}"
                loadActiveLoans() // Оновлюємо список після успіху
            } else if (result is Result.Error) {
                _message.value = result.message
            }
            _isLoading.value = false
        }
    }
}