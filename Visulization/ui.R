library(shiny)

library(ggplot2)  # for jobs dataset 

data = read.csv("alljobs1.csv",header = TRUE)
names(data)[1] <- "Source"

jobs = data[-c(2)]
jobs = jobs[c("Source","Company","Title","City","State","Link")]
top_companies = read.csv("companies.csv",header = TRUE)
top_cities =  read.csv("cities.csv",header = TRUE)

shinyUI(fluidPage(
  title = 'DataTables of Jobs',
  sidebarLayout(
    sidebarPanel(
      conditionalPanel(
        'input.dataset === "jobs"',
        checkboxGroupInput('show_vars', 'Columns in job list to how:',
                           names(jobs), selected = names(jobs))
      ),
      conditionalPanel(
        'input.dataset === "top_companies"',
        helpText('Click the column header to sort a column.')
      ),
      conditionalPanel(
        'input.dataset === "top_cities"',
        helpText('Display 5 records by default.')
      )
    ),
    
    mainPanel(
      tabsetPanel(
        id = 'dataset',
        tabPanel('jobs', dataTableOutput('mytable1')),
        tabPanel('top_companies', dataTableOutput('mytable2')),
        tabPanel('top_cities', dataTableOutput('mytable3'))
      )
    )
  )
))