package com.example.apz.presentation.ui.catalog

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.apz.data.models.BookResponse
import com.example.apz.presentation.viewmodel.BookViewModel
import androidx.compose.material3.ExperimentalMaterial3Api
import com.example.apz.presentation.viewmodel.ReservationViewModel

@Composable
fun BookListScreen(
    bookViewModel: BookViewModel = viewModel(),
    reservationViewModel: ReservationViewModel = viewModel(),
    onBookClick: (BookResponse) -> Unit
) {
    var searchQuery by remember { mutableStateOf("") }
    val books by bookViewModel.books.collectAsState()
    val isLoading by bookViewModel.isLoading.collectAsState()
    val reservationMessage by reservationViewModel.message.collectAsState()

    LaunchedEffect(Unit) {
        bookViewModel.searchBooks("")
    }

    // Показуємо Snackbar для бронювання
    if (reservationMessage != null) {
        Snackbar(
            modifier = Modifier.padding(8.dp),
            action = {
                TextButton(onClick = { reservationViewModel.clearMessage() }) {
                    Text("OK")
                }
            }
        ) {
            Text(reservationMessage ?: "")
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        OutlinedTextField(
            value = searchQuery,
            onValueChange = {
                searchQuery = it
                bookViewModel.searchBooks(it)
            },
            label = { Text("Пошук книг...") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            singleLine = true,
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Text("✕")
                    }
                }
            }
        )

        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else if (books.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("Книг не знайдено")
                    Text("Спробуйте інший пошук", style = MaterialTheme.typography.bodySmall)
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(books) { book ->
                    BookItem(
                        book = book,
                        onClick = { onBookClick(book) },
                        onReserveClick = {
                            reservationViewModel.reserveBook(book.book_id)
                        }
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BookItem(
    book: BookResponse,
    onClick: () -> Unit, // Для переходу в деталі (якщо буде)
    onReserveClick: (Int) -> Unit // Новий колбек для бронювання
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = book.title,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = book.author,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                // Кнопка бронювання (тільки якщо доступна)
                if (book.status == "available") {
                    Button(
                        onClick = { onReserveClick(book.book_id) },
                        modifier = Modifier.height(36.dp)
                    ) {
                        Text("📌")
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Статус: ${book.status}",
                style = MaterialTheme.typography.bodySmall,
                color = when (book.status) {
                    "available" -> MaterialTheme.colorScheme.primary
                    "issued" -> MaterialTheme.colorScheme.error
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                }
            )
        }
    }
}