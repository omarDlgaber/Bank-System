# --------- Import Libraries ---------
import random
import sqlite3 as sql
import datetime

# --------- Create All Dataset ---------
# Single connection to persistent database     
db = sql.connect("Bank System.db")
cr = db.cursor()
# Create tables if they do not exist
# Create tables
cr.execute("CREATE TABLE IF NOT EXISTS 'Admin' (Username TEXT, Password TEXT)")

cr.execute("""CREATE TABLE IF NOT EXISTS 'Client Account' (
    Name TEXT,
    Nationality TEXT,
    Gender TEXT,
    'Phone Number' TEXT,
    'Document Submit' TEXT,
    'Account Type' TEXT,
    Balance INTEGER,
    Password TEXT,
    'Bank Account Number' INTEGER,
    Time TEXT
)""")

cr.execute("""CREATE TABLE IF NOT EXISTS 'Account Transactions' (
    Name TEXT,
    'Bank Account Number' INTEGER,
    'Transaction Type' TEXT,
    Amount INTEGER,
    Balance INTEGER,
    History TEXT
    )""")

db.commit()



# ------------------------------------------------
# -------------- Transaction Class ---------------
# ------------------------------------------------

class Transaction:
    def __init__(self, name, bank_account_number, trans_type, amount, balance):
        self.name = name
        self.bank_account_number = bank_account_number
        self.trans_type = trans_type
        self.amount = amount
        self.balance = balance
        # Generate a timestamp for the transaction
        # datetime.datetime.now() returns the current local date and time
        self.history = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_to_db()

    def save_to_db(self):             # This method save the transaction details to the DB
        cr.execute("""
            INSERT INTO 'Account Transactions' (Name, 'Bank Account Number', 'Transaction Type', Amount, Balance, History)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.name, self.bank_account_number, self.trans_type, self.amount, self.balance, self.history))
        db.commit()
    
    
    @ staticmethod
    def deposit(account, deposit_amount):
        if deposit_amount < 0:
            print("❌ Invalid operation")
        else:
            new_balance = deposit_amount + account.get_balance()
            account.set_balance(new_balance)
            # Here, the Transaction is recorded for the deposit or save the transaction details
            Transaction(account.name, account.bank_account_number, "Deposit", deposit_amount, new_balance)
            print(f"✅ Deposit successful. New balance: {new_balance}")
            
            return account.get_balance()    # Return the new balance after deposit
    
    
    @ staticmethod
    def withdraw(account, withdraw_amount):
        # Determine the minimum allowed balance based on account type
        # isinstance() function returns True if the specified object is of the specified type, otherwise False
        if isinstance(account, CurrentAccount):
            mini_amount = CurrentAccount.mini_amount
        elif isinstance(account, SavingAccount):
            mini_amount = SavingAccount.mini_amount
        else:
            mini_amount = 0  # Default or error case

        if withdraw_amount <= 0: # Added check for non-positive withdraw amount
            print("❌ Invalid operation: Withdraw amount must be positive.")
        elif account.get_balance() - withdraw_amount < mini_amount: # Check if withdraw will go below min_amount
            print("There is not enough balance in your account or it would fall below the minimum allowed.")
        else:
            new_balance = account.get_balance() - withdraw_amount
            account.set_balance(new_balance)
            Transaction(account.name, account.bank_account_number, "Withdraw", withdraw_amount, new_balance)
            print(f"✅ Withdraw successful. New balance: {new_balance}")
            return account.get_balance()
    
    
    @ staticmethod
    def transfer(sender_account, receiver_account, transfer_amount):
        if transfer_amount <= 0:
            print("❌ Invalid transfer amount")
            return
        # Ensure sender account has enough balance, considering its minimum amount
        if isinstance(sender_account, CurrentAccount):
            sender_min_amount = CurrentAccount.mini_amount
        elif isinstance(sender_account, SavingAccount):
            sender_min_amount = SavingAccount.mini_amount
        else:
            sender_min_amount = 0
        
        if sender_account.get_balance() - transfer_amount < sender_min_amount:
            print("❌ Insufficient balance or transfer would fall below minimum allowed.")
            return
        
        sender_account.set_balance(sender_account.get_balance() - transfer_amount)
        Transaction(sender_account.name, sender_account.bank_account_number, "Transfer Sent", transfer_amount, sender_account.get_balance())
        
        receiver_account.set_balance(receiver_account.get_balance() + transfer_amount)
        Transaction(receiver_account.name, receiver_account.bank_account_number, "Transfer Received", transfer_amount, receiver_account.get_balance())
        
        print(f"✅ Transfer of {transfer_amount} successful. New balance: {sender_account.get_balance()}")
        return sender_account.get_balance()
    
    
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------- ClientAccount --------------------------------
class ClientAccount:
    def __init__(self, name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number):
        self.name = name
        self.nationality = nationality
        self.gender = gender 
        self.phone_number = phone_number
        self._document_submit = document_submit
        self.account_type = account_type
        self.__balance = balance
        self.__password = password
        self.bank_account_number = bank_account_number

    def get_balance(self):
        return self.__balance

    def set_balance(self, new_balance):
        self.__balance = new_balance

    def get_password(self):
        return self.__password

    def set_clientPassword(self, new_password):
        self.__password = new_password

    # Added a static method to load a client account type from the database
    @staticmethod
    def load_account_from_db(bank_account_number):
        cr.execute("""SELECT Name, Nationality, Gender, "Phone Number", "Document Submit", "Account Type", Balance, Password, "Bank Account Number" FROM "Client Account" WHERE "Bank Account Number" = ?""", (bank_account_number,))
        account_data = cr.fetchone()

        if account_data:
            # Unpack the account data
            # Ensure the order matches the SELECT statement above
            name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number_db = account_data
            
            if account_type == "Current":
                return CurrentAccount(name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number_db)
            elif account_type == "Saving":
                return SavingAccount(name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number_db)
        

# ------------------------- CurrentAccount --------------------------------
class CurrentAccount(ClientAccount):
    mini_amount = 2500

    def __init__(self, name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number):
        super().__init__(name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number)

    def deposit(self, deposit_amount):
        Transaction.deposit(self, deposit_amount)
        # Update balance in DB after transaction
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (self.get_balance(), self.bank_account_number))
        db.commit()

    def withdraw(self, withdraw_amount):
        Transaction.withdraw(self, withdraw_amount)
        # Update balance in DB after transaction
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (self.get_balance(), self.bank_account_number))
        db.commit()

    def transfer(self, receiver_account, transfer_amount):
        Transaction.transfer(self, receiver_account, transfer_amount)
        # Update balances in DB after transfer
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (self.get_balance(), self.bank_account_number))
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (receiver_account.get_balance(), receiver_account.bank_account_number))
        db.commit()


# ------------------------- SavingAccount --------------------------------
class SavingAccount(ClientAccount):
    mini_amount = 3000

    def __init__(self, name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number, interest=0.12):
        super().__init__(name, nationality, gender, phone_number, document_submit, account_type, balance, password, bank_account_number)
        self.interest = interest

    def deposit(self, deposit_amount):
        Transaction.deposit(self, deposit_amount)
        # Update balance in DB after transaction
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (self.get_balance(), self.bank_account_number))
        db.commit()

    def withdraw(self, withdraw_amount):
        # Saving accounts typically do not allow direct withdrawals.
        print("You can not withdraw money directly from Saving Account.")
    
    
    def apply_interest(self):
        amount_with_interest = self.get_balance() * self.interest
        new_balance = self.get_balance() + amount_with_interest
        self.set_balance(new_balance)
        # Here, the Transaction is recorded for the interest application
        Transaction(self.name, self.bank_account_number, "Interest", amount_with_interest, new_balance)
        print(f"✅ Interest applied. New balance: {new_balance}")
        # Update balance in DB after interest application
        cr.execute('UPDATE "Client Account" SET Balance = ? WHERE "Bank Account Number" = ?', (self.get_balance(), self.bank_account_number))
        db.commit()



# ------------------------- Admin class --------------------------------
class BankAdmin() :
    
    def __init__(self, adminUsername='admin', adminPassword='123'):
        self.adminUsername = adminUsername 
        self.adminPassword = adminPassword
        # self.saveAdminDB()  # This should ideally be called once if the admin already exists, not every time an object is created.
        # For simplicity in this example, we'll keep it, but in a real app, check if admin exists first.
        # Check if admin credentials already exist before inserting
        cr.execute("SELECT Username FROM 'Admin' WHERE Username = ?", (self.adminUsername,))
        if not cr.fetchone():
            cr.execute("INSERT INTO 'Admin' (Username, Password) VALUES (?, ?)", (self.adminUsername, self.adminPassword))
            db.commit()
    
    # ------------------------- Create Client Account -------------------------------
    # This method creates a new client account after validating the inputs
    def createClientAccount(self):
        
        name = input("Full Name: ").title()
        nationality = input("Nationality: ").title()
        gender = input("Gender: ").capitalize()
        
        # ----------- To Check if the phone number is valid -----------------
        
        known_provider = ("010", "011", "012", "015")
        
        # Check if the phone number is valid
        while True:
            phone_number = input("Phone Number: ")
            
            if not (len(phone_number) == 11 and phone_number.startswith("01") and phone_number.isdigit()):
                print("Invalid Phone Number ❌, try again")
                continue
            
            if not phone_number.startswith(known_provider):
                print("Invalid Phone Number ❌ (Unknown provider), try again")
                continue
            break
        
        print("Phone Number Accepted ✅")
        
        
        document_submit = input("Document Submit: ").title()
        account_type = input("Account Type (Current/Saving): ").capitalize()
        
        # ----------- Check initial balance ----------------        
        while True:
            
            init_balance = float(input("Initial Balance: "))
            if account_type.capitalize() == "Current" :
                if init_balance >= CurrentAccount.mini_amount :
                    print("✅ Valid Balance")
                    break
                
                else:
                    print("❌ Invalid amount: Initial balance for Current Account must be at least", CurrentAccount.mini_amount)
                    continue
                
                
            elif account_type.capitalize() == "Saving" :
                if init_balance >= SavingAccount.mini_amount :
                    print("✅ Valid Balance")
                    break
                
                else:
                    print("❌ Invalid amount: Initial balance for Saving Account must be at least", SavingAccount.mini_amount)
                    continue
                
            else:
                print("❌ Invalid account type. Please choose 'Current' or 'Saving'.")
                continue
            
            
            
        password = input("Password: ")
        # ------------ To Confirm password ----------------
        while True :
            confirm_password = input("Confirm password: ")
            if confirm_password == password :
                print("Password Created ✅")
                break
            else :
                print("Password is not match ❌")
                
        
        # ------------ Create the account number ----------------
        # ------------ Generate a random 4-digit bank account number ------------------
        
        bank_account_number = random.randrange(1000, 9999)
        
        
        # ------------- Create Current Account ----------------
        if account_type.capitalize() == "Current" :
            new_account = CurrentAccount(name, nationality, gender, phone_number, document_submit, account_type, init_balance, password, bank_account_number)
            return new_account
        # ------------- Create Saving Account ----------------
        elif account_type.capitalize() == "Saving" :
            new_account = SavingAccount(name, nationality, gender, phone_number, document_submit, account_type, init_balance, password, bank_account_number)
            return new_account
        
        
    def Delete_Client_Account(self, dele_clientName, dele_clientAccount) :
        
        # Verify the account exists and matches the name before deleting
        cr.execute("SELECT `Name` FROM `Client Account` WHERE Name = ? AND `Bank Account Number` = ?", (dele_clientName, dele_clientAccount))
        account_to_delete = cr.fetchone()
        
        if account_to_delete:
            cr.execute("DELETE FROM `Client Account` WHERE Name = ? AND `Bank Account Number` = ?", (dele_clientName, dele_clientAccount))
            db.commit()
            # Delete the transactions related to this account
            # Corrected table name from 'Transactions Account' to 'Account Transactions'
            cr.execute("DELETE FROM `Account Transactions` WHERE `Bank Account Number` = ?", (dele_clientAccount,))
            db.commit()
            print("✅ The Account Has Been Deleted")
        else :
            print("❌ Enter The Client Name and Bank number Correctly. Account not found.")
        # return
    
    # Corrected method definition by adding 'self'
    def checkAccountSummary(self, client_name_summary, bank_number_summary):
    
        # --- TO get name and bank account number from DB ----
        cr.execute("""SELECT Name, Gender, Nationality, "Phone Number", "Account Type", "Bank Account Number", Balance, Time
        FROM 'Client Account' WHERE Name = ? AND "Bank Account Number" = ?""", (client_name_summary, bank_number_summary))
        # make a Fetch for all data from DB
        summary_data = cr.fetchone()
        
        print("Client Information Summary".center(50, "-"))
        
        if summary_data:
            # This list of labels has been REORDERED to EXACTLY MATCH the SELECT statement above.
            
            columns = [
                'Name',
                'Gender',
                'Nationality',
                'Phone Number',
                'Account Type',
                'Bank Account Number',
                'Balance',
                'Time'
                ]
            # The zip function will now pair the correct label with the correct value.
            for col_name, value in zip(columns, summary_data):
                print(f"{col_name}: {value}")
            
        else: 
            print("❌ Enter client name and Bank Account Number correctly")



# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------ Main Application ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Interface ------------------------------------------------
def Insert_Client_Account(new_account):
    if not new_account: # Handle cases where account creation failed
        print("Error: Account object is None, cannot insert into DB.")
        return

    cr.execute("""INSERT INTO 'Client Account' (Name, Nationality, Gender, 'Phone Number', 'Document Submit', 'Account Type', Balance, Password, 'Bank Account Number', Time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_account.name,
                        new_account.nationality,
                        new_account.gender,
                        new_account.phone_number,
                        new_account._document_submit,
                        new_account.account_type,
                        new_account.get_balance(),
                        new_account.get_password(),
                        new_account.bank_account_number,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Format time correctly
                    ))
    db.commit()
    
    # Fetching the account that was just created...
    # We can fetch directly using the bank_account_number which is known
    cr.execute("""SELECT Name, Gender, Nationality, "Phone Number", "Account Type", "Bank Account Number", Balance, Time FROM 'Client Account' WHERE "Bank Account Number" = ?""", (new_account.bank_account_number,))
    last_account_created = cr.fetchone()
    
    print("Client Information Summary".center(50, "-"))
    
    if last_account_created:
        columns = [
            'Name',
            'Gender',
            'Nationality',
            'Phone Number',
            'Account Type',
            'Bank Account Number',
            'Balance',
            'Time'
        ]
        # Iterate and print all details, do not return inside the loop
        for col_name, value in zip(columns, last_account_created):
            print(f"{col_name}: {value}")
    else:
        print("Error: Could not retrieve the created account from the database.")


def Check_Account_Balance(login_clientAccountNum):
    
    
    cr.execute("""SELECT "Account Type", Balance FROM 'Client Account' WHERE "Bank Account Number" = ?""", (login_clientAccountNum,))
    balance_data = cr.fetchone()
    
    print("Client Information Balance".center(50, "-"))
    
    if balance_data:
        column = ['Account Type', 'Balance']
        for col_name, value in zip(column, balance_data):
            print(f"{col_name}: {value}")
    else: 
        print("❌ Account Number not found.")
# ------------------------------------------------------------------------------------

# Create a single BankAdmin instance when the script starts
bank_admin = BankAdmin('admin', '123') 

while True :
    
    # Displaying the welcome message and options
    print(" Welcome to Bank System ".center(50,'='))
    print("""Choose your portal : 
            1. Bank Admin
            2. Client Account
            3. Close Application
            """)
    portal = int(input("Enter your portal choice (1, 2 or 3): "))
    
    if portal == 1 : # Admin portal
        cr.execute('SELECT "Username", "Password" FROM "Admin"')
        admin_fetch = cr.fetchall()
        
        # admin_authenticated = False
        # for _ in range(3): # Give admin 3 tries to login
        print("Admin Login".center(50, "-"))
        while True:
            adminUsername = input('Username : ')
            adminPassword = input('Password : ')
            
            
            for admin_row in admin_fetch:
                if admin_row[0] == adminUsername and admin_row[1] == adminPassword:
                    # admin_authenticated = True
                    print("✅ Username and Password are correct")
                    break      # If input match, break the loop
                
            
                
            else:      # If no match found, print error message
                print("❌ Wrong username or password, please try again")
                continue # Go back to the admin login prompt
            break   # Exit the while loop after one attempt
        
        print("Welcome to Admin Portal".center(50, "-"))
        
        while True:
            print("""\nAdmin Menu:
                        1. Create Bank Account
                        2. Delete Bank Account
                        3. Check Account summary
                        4. Exit (Logout)""")
            admin_action = int(input("Select your option : "))
            
            if admin_action == 1:
                # Create the client account using the bank_admin instance
                new_client_account = bank_admin.createClientAccount()
                if new_client_account:
                    Insert_Client_Account(new_client_account) 
                else:
                    print("❌ Account creation failed. Please check input details.")
            
            elif admin_action == 2:
                print("Delete Client Account".center(50,'='))
                dele_clientName = input("Client Name: ").title()
                dele_clientAccount = int(input("Account Number: "))
                bank_admin.Delete_Client_Account(dele_clientName, dele_clientAccount)
            
            elif admin_action == 3:
                print("Check Account Summary".center(50,'='))
                client_name_summary = input("The client name: ").title()
                bank_number_summary = int(input("Enter Bank Account Number: "))
                bank_admin.checkAccountSummary(client_name_summary, bank_number_summary)
            
            elif admin_action == 4:
                print("Logging out from Admin Portal.")
                break # Exit admin menu loop
            else:     # Invalid option
                print("Invalid option. Please try again.")
    # -----------------------------------------------
    # ---------------- Client portal ----------------
    elif portal == 2 : 
        print("Client Login".center(50, "-"))
        cr.execute("SELECT `Bank Account Number`, Password FROM `Client Account`")
        dataLogin_fetch = cr.fetchall()
        # print(dataLogin_fetch)  # Debugging line to see fetched login data
        
        
        login_clientAccountNum = int(input("Account Number : "))
        login_clientPass = input("Password : ")
        logged_in_client_account = ClientAccount.load_account_from_db(login_clientAccountNum)   # Load the account object from the database and client account type
        print(logged_in_client_account)
            
            # Load the account object if credentials match
        for dataLog_row in dataLogin_fetch:
            if dataLog_row[0] == login_clientAccountNum and dataLog_row[1] == login_clientPass:
                
                # If the account is found, break the loop
                if logged_in_client_account:
                    print(f"Welcome {logged_in_client_account.name}".center(50, "*"))
                    break # Exit the inner for loop
            
            
        else:
            print("❌ Wrong Account Number or Password, please try again")
        
        
        while True:
            print("Client Menu".center(50, "-"))
            print("""
                    1. Check Balance
                    2. Deposit Money
                    3. Withdraw Money
                    4. Transfer Money
                    5. Interest Application (Saving Account Only)
                    6. Transaction History
                    7. Exit (Logout)
                    """)
            
            try:
                client_action = int(input("Select your option : "))
            except ValueError:      # Handle non-integer input
                print("Invalid input. Please enter a number between 1 and 7.")   # This will catch any non-integer input
                continue
            if client_action == 1:
                Check_Account_Balance(login_clientAccountNum)
            
            elif client_action == 2:
                try:
                    amount = float(input("Enter amount to deposit: "))
                    logged_in_client_account.deposit(amount)
                except ValueError:  # ValueError: if the input is not a valid float
                    print("Invalid amount. Please enter a number.")
            
            elif client_action == 3:
                try:
                    amount = float(input("Enter amount to withdraw: "))
                    logged_in_client_account.withdraw(amount)
                except ValueError:
                    print("Invalid amount. Please enter a number.")
            
            elif client_action == 4:
                try:
                    transfer_to_accNum = int(input("Enter the account number you want to transfer to: "))
                    transfer_amount = float(input("Enter amount to transfer: "))
                    
                    receiver_account = ClientAccount.load_account_from_db(transfer_to_accNum)  # 
                    
                    if receiver_account:
                        logged_in_client_account.transfer(receiver_account, transfer_amount)
                    else:
                        print("⚠️ The receiver account not found.")
                except ValueError:
                    print("Invalid input. Please enter numbers for account number and amount.")
            
            # Check if the client action is for interest application
            elif client_action == 5:
                if isinstance(logged_in_client_account, SavingAccount):
                    logged_in_client_account.apply_interest()
                else:
                    print("❌ Interest application is only available for Saving Accounts.")
            
            
            
            elif client_action == 6:
                print("Transaction History".center(50, "-"))
                cr.execute("""SELECT * FROM "Account Transactions" WHERE "Bank Account Number" = ?""", (logged_in_client_account.bank_account_number,))
                account_transactions = cr.fetchall()
                
                if account_transactions:
                    # Define column names for better readability
                    transaction_columns = ['Name', 'Bank Account Number', 'Transaction Type', 'Amount', 'Balance After', 'Timestamp']
                    for transaction_row in account_transactions:
                        print("-" * 30) # Separator for each transaction
                        for col_name, value in zip(transaction_columns, transaction_row):
                            print(f"{col_name}: {value}")
                else:
                    print("No transactions found for this account.")
            
            elif client_action == 7:
                print("Logging out from Client Portal.")
                break # Exit client menu loop
            else:
                print("Invalid option. Please try again.")
    
    elif portal == 3:
        print("Closing application. Goodbye!")
        db.close() # Close database connection before exiting
        break # Exit main application loop
    
    else:
        print("Invalid portal choice. Please enter 1, 2, or 3.")