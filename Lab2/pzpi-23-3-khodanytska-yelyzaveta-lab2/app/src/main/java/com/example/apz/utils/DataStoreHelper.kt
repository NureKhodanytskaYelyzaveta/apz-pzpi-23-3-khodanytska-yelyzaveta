package com.example.apz.utils

import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

// Розширення для створення DataStore
val Context.dataStore by preferencesDataStore(name = "app_settings")

object DataStoreHelper {
    private val USER_ID_KEY = intPreferencesKey(Constants.USER_ID_KEY)
    private val USER_NAME_KEY = stringPreferencesKey(Constants.USER_NAME_KEY)
    private val USER_EMAIL_KEY = stringPreferencesKey(Constants.USER_EMAIL_KEY)
    private val USER_ROLE_KEY = stringPreferencesKey(Constants.USER_ROLE_KEY)

    suspend fun saveUserSession(context: Context, id: Int, name: String, email: String, role: String) {
        context.dataStore.edit { prefs ->
            prefs[USER_ID_KEY] = id
            prefs[USER_NAME_KEY] = name
            prefs[USER_EMAIL_KEY] = email
            prefs[USER_ROLE_KEY] = role
        }
    }

    suspend fun getUserId(context: Context): Int? {
        return context.dataStore.data.first()[USER_ID_KEY]
    }

    fun getUserSessionFlow(context: Context): Flow<UserSession?> {
        return context.dataStore.data.map { prefs ->
            val id = prefs[USER_ID_KEY]
            if (id != null) {
                UserSession(
                    id = id,
                    name = prefs[USER_NAME_KEY] ?: "",
                    email = prefs[USER_EMAIL_KEY] ?: "",
                    role = prefs[USER_ROLE_KEY] ?: ""
                )
            } else null
        }
    }

    suspend fun clearSession(context: Context) {
        context.dataStore.edit { it.clear() }
    }
}

data class UserSession(val id: Int, val name: String, val email: String, val role: String)