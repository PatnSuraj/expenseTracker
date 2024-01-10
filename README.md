# Expense Tracker Application

Expense Tracker is a simple web application built using Flask, a Python web framework. It allows users to log their expenses, view their total expenses, visualize expense distribution by category, edit or delete individual expenses, and export expense data to a CSV file.

# Features

User Authentication: Users can register, log in, and log out to access personalized expense tracking. The authentication system now provides an error message when the user enters an incorrect username or password.

Expense Logging: Users can log their expenses by providing details such as amount, category, and description. New updates include the ability to filter and sort expenses based on the amount in ascending or descending order.

Total Expense View: Users can view their total expenses along with a detailed list of individual expenses. The total expense calculation is now more robust, and data is stored even when the user logs out.

Expense Distribution Visualization: The application generates a pie chart to visualize expense distribution by category. Users can now filter and sort expenses based on amount to get a clearer picture of their spending patterns.

Editing and Deleting Expenses: Users can edit the details of a logged expense or delete it entirely, providing more control over their recorded data.

CSV Export: Users can export their expense data to a CSV file for external use or record-keeping. The exported CSV now includes the additional filtered and sorted data.

User Profile Dropdown: A user profile dropdown has been added, displaying the logged-in username. It provides options to edit the user profile, change the password, and logout.

Data Persistence: Expense data is now persistent, ensuring that data gets stored even when the user logs out, allowing for a seamless user experience.

# Dependencies
Flask
SQLite
Matplotlib
Pandas
