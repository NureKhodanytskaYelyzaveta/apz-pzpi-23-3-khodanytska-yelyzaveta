package com.example.apz.presentation.ui.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.apz.presentation.viewmodel.AuthViewModel

@Composable
fun ProfileScreen(
    viewModel: AuthViewModel = viewModel(),
    onLogout: () -> Unit
) {
    val session by viewModel.session.collectAsState()

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        // 🔹 Контент
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(32.dp))

            Text(
                text = "👤 Особистий кабінет",
                style = MaterialTheme.typography.headlineMedium
            )

            Spacer(modifier = Modifier.height(48.dp))

            session?.let { user ->
                OutlinedCard(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {

                        Text("Ім'я:")
                        Text(user.name, modifier = Modifier.padding(bottom = 16.dp))

                        Text("Email:")
                        Text(user.email, modifier = Modifier.padding(bottom = 16.dp))

                        Text("Роль:")
                        Text(user.role)
                    }
                }
            }

            Spacer(modifier = Modifier.height(100.dp)) // щоб не налазило під кнопку
        }

        // 🔻 Кнопка ІДЕАЛЬНО по центру знизу
        Button(
            onClick = onLogout,
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.errorContainer,
                contentColor = MaterialTheme.colorScheme.onErrorContainer
            )
        ) {
            Text("🚪 Вийти з акаунту")
        }
    }
}