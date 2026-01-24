package com.dimitry4now

import com.dimitry4now.model.InfoResponse
import com.dimitry4now.model.Student
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.delay
import java.time.LocalDate

fun Application.configureRouting() {
  val machineName = System.getenv("MACHINE_NAME") ?: "machineX"
  val machineEnabled = System.getenv("MACHINE_ENABLED")?.toBoolean() ?: true
  val student = Student("Dimitar", "Betinski", "175030")
  val targetPrimes = System.getenv("TARGET_PRIMES")?.toInt() ?: 200

  routing {
    fun isPrime(n: Long): Boolean {
      if (n < 2) return false
      if (n % 2L == 0L) return n == 2L
      var i = 3L
      while (i * i <= n) {
        if (n % i == 0L) return false
        i += 2
      }
      return true
    }

    get("/work-cpu-bound") {
      val rnd = java.util.Random()
      var primesFound = 0
      val targetPrimes = targetPrimes

      while (primesFound < targetPrimes) {
        val candidate = rnd.nextLong(10_000_000L, 50_000_000L)
        if (isPrime(candidate)) {
          primesFound++
        }
      }

      call.respond(
        InfoResponse(
          student = student,
          date = LocalDate.now().toString(),
          machine = machineName
        )
      )
    }

    get("/health") {
      if (machineEnabled) {
        call.respondText("OK")
      } else {
        call.respondText("DOWN", status = io.ktor.http.HttpStatusCode.ServiceUnavailable)
      }
    }
  }
}
