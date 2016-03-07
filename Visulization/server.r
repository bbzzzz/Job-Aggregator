library(shiny)

data = read.csv("alljobs1.csv",header = TRUE)
names(data)[1] <- "Source"

jobs = data[-c(2)]
top_companies = read.csv("companies.csv",header = TRUE)
top_cities =  read.csv("cities.csv",header = TRUE)

shinyServer(function(input, output) {
  
  # a large table, reative to input$show_vars
  output$mytable1 <- renderDataTable({
    library(ggplot2)
    jobs[, input$show_vars, drop = FALSE]
  })
  
  # sorted columns are colored now because CSS are attached to them
  output$mytable2 <- renderDataTable({
    top_companies
  }, options = list(orderClasses = TRUE))
  
  # customize the length drop-down menu; display 10 rows per page by default
  output$mytable3 <- renderDataTable({
    top_cities
  }, options = list(lengthMenu = c(10,20), pageLength = 10))
  
})

