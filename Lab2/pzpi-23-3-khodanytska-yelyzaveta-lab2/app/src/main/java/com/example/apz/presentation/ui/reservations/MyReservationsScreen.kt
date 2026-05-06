package com.example.apz.presentation.ui.reservations

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.apz.data.models.ReservationResponse
import com.example.apz.presentation.viewmodel.ReservationViewModel
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun MyReservationsScreen(
    viewModel: ReservationViewModel = viewModel(),
    onReservationCancelled: () -> Unit = {} // ✅ Новий параметр
) {
    val reservations by viewModel.reservations.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val message by viewModel.message.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadActiveReservations()
    }

    // ✅ Коли бронювання скасовано, повідомляємо батьківський екран
    LaunchedEffect(message) {
        if (message == "Бронювання скасовано") {
            onReservationCancelled()
            viewModel.clearMessage()
        }
    }


    Column(modifier = Modifier.fillMaxSize()) {
        Text(
            text = "📌 Мої бронювання",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(16.dp)
        )

        message?.let { msg ->
            Snackbar(
                modifier = Modifier.padding(8.dp),
                action = {
                    TextButton(onClick = { viewModel.clearMessage() }) {
                        Text("Закрити")
                    }
                }
            ) {
                Text(msg)
            }
        }

        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (reservations.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("У вас немає активних бронювань")
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(reservations) { reservation ->
                    ReservationItem(
                        reservation = reservation,
                        onCancelClick = {
                            viewModel.cancelReservation(reservation.reservation_id)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun ReservationItem(
    reservation: ReservationResponse,
    onCancelClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "ID бронювання: ${reservation.reservation_id}",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "ID книги: ${reservation.book_id}",
                style = MaterialTheme.typography.bodyMedium
            )
            Text(
                text = "Дійсне до: ${formatDate(reservation.expiry_date)}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = onCancelClick,
                modifier = Modifier.align(Alignment.End),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Text("Скасувати")
            }
        }
    }
}

fun formatDate(dateString: String): String {
    return try {
        val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        val outputFormat = SimpleDateFormat("dd.MM.yyyy", Locale.getDefault())
        val date = inputFormat.parse(dateString)
        outputFormat.format(date)
    } catch (e: Exception) {
        dateString
    }
}