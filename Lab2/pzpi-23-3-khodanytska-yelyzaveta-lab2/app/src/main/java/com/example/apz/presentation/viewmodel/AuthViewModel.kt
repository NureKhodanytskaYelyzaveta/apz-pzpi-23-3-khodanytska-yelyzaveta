package com.example.apz.presentation.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.apz.data.repository.LibraryRepository
import com.example.apz.utils.DataStoreHelper
import com.example.apz.utils.UserSession
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = LibraryRepository(application)

    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private val _session = MutableStateFlow<UserSession?>(null)
    val session: StateFlow<UserSession?> = _session.asStateFlow()

    init {
        checkSession()
    }

    private fun checkSession() {
        viewModelScope.launch {
            DataStoreHelper.getUserSessionFlow(getApplication()).collect { user ->
                _session.value = user
            }
        }
    }

    fun login(email: String, password: String) {
        _authState.value = AuthState.Loading

        viewModelScope.launch {
            val result = repository.login(email, password)

            when (result) {
                is com.example.apz.utils.Result.Success -> {
                    _authState.value = AuthState.Success
                }
                is com.example.apz.utils.Result.Error -> {
                    _authState.value = AuthState.Error(result.message)
                }
                com.example.apz.utils.Result.Loading -> Unit
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            repository.logout()
            _session.value = null
            _authState.value = AuthState.LoggedOut
        }
    }
}

sealed class AuthState {
    object Idle : AuthState()
    object Loading : AuthState()
    object Success : AuthState()
    data class Error(val message: String) : AuthState()
    object LoggedOut : AuthState()
}