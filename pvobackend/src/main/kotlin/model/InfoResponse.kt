package com.dimitry4now.model

import kotlinx.serialization.Serializable

@Serializable
data class InfoResponse(
  val student: Student,
  val date: String,
  val machine: String
)
