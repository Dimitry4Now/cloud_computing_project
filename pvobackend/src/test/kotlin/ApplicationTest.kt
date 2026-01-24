package com.dimitry4now

import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlin.test.Test
import kotlin.test.assertTrue

class ApplicationTest {

    @Test
    fun testRoot() = testApplication {
        application {
            module()
        }
        val response = client.get("/health")

        assertTrue(
          response.status == HttpStatusCode.OK || response.status == HttpStatusCode.ServiceUnavailable,
          "Expected status OK or ServiceUnavailable but was ${response.status}"
        )
    }

}
