package com.dimitry4now.model

import kotlinx.serialization.Serializable

@Serializable
data class Student(
  val name: String,
  val surname: String,
  val index: String
)
