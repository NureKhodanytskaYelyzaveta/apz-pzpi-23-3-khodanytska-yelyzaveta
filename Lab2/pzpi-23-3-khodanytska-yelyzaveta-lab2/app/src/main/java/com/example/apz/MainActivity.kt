package com.example.apz

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.apz.presentation.ui.auth.LoginScreen
import com.example.apz.presentation.ui.catalog.BookListScreen
import com.example.apz.presentation.ui.loans.MyLoansScreen
import com.example.apz.presentation.ui.profile.ProfileScreen
import com.example.apz.presentation.ui.reservations.MyReservationsScreen
import com.example.apz.presentation.viewmodel.*
import com.example.apz.ui.theme.APZTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            APZTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    LibraryApp()
                }
            }
        }
    }
}

@Composable
fun LibraryApp() {
    val authViewModel: AuthViewModel = viewModel()
    val session by authViewModel.session.collectAsState()

    var currentScreen by remember { mutableStateOf<Screen>(Screen.Login) }

    LaunchedEffect(session) {
        currentScreen = if (session != null) Screen.Catalog else Screen.Login
    }

    when (currentScreen) {
        is Screen.Login -> {
            LoginScreen(
                onLoginSuccess = { currentScreen = Screen.Catalog }
            )
        }

        is Screen.Catalog,
        is Screen.Loans,
        is Screen.Profile,
        is Screen.Reservations -> {
            MainNavigation(
                currentScreen = currentScreen,
                onNavigate = { currentScreen = it },
                onLogout = {
                    authViewModel.logout()
                    currentScreen = Screen.Login
                }
            )
        }
    }
}

@Composable
fun MainNavigation(
    currentScreen: Screen,
    onNavigate: (Screen) -> Unit,
    onLogout: () -> Unit
) {
    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Text("📚") },
                    label = { Text("Каталог") },
                    selected = currentScreen is Screen.Catalog,
                    onClick = { onNavigate(Screen.Catalog) }
                )
                NavigationBarItem(
                    icon = { Text("📌") },
                    label = { Text("Бронь") },
                    selected = currentScreen is Screen.Reservations,
                    onClick = { onNavigate(Screen.Reservations) }
                )
                NavigationBarItem(
                    icon = { Text("📖") },
                    label = { Text("Позики") },
                    selected = currentScreen is Screen.Loans,
                    onClick = { onNavigate(Screen.Loans) }
                )
                NavigationBarItem(
                    icon = { Text("👤") },
                    label = { Text("Профіль") },
                    selected = currentScreen is Screen.Profile,
                    onClick = { onNavigate(Screen.Profile) }
                )
            }
        }
    ) { paddingValues ->

        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues) // 🔥 головне виправлення
        ) {
            when (currentScreen) {

                is Screen.Catalog -> {
                    val bookViewModel: BookViewModel = viewModel()
                    val reservationViewModel: ReservationViewModel = viewModel()

                    BookListScreen(
                        bookViewModel = bookViewModel,
                        reservationViewModel = reservationViewModel,
                        onBookClick = { }
                    )
                }

                is Screen.Loans -> {
                    val loanViewModel: LoanViewModel = viewModel()
                    MyLoansScreen(viewModel = loanViewModel)
                }

                is Screen.Profile -> {
                    ProfileScreen(
                        onLogout = onLogout
                    )
                }

                is Screen.Reservations -> {
                    val reservationViewModel: ReservationViewModel = viewModel()
                    val bookViewModel: BookViewModel = viewModel()

                    MyReservationsScreen(
                        viewModel = reservationViewModel,
                        onReservationCancelled = {
                            bookViewModel.searchBooks("")
                        }
                    )
                }

                else -> {}
            }
        }
    }
}

sealed class Screen {
    object Login : Screen()
    object Catalog : Screen()
    object Loans : Screen()
    object Profile : Screen()
    object Reservations : Screen()
}