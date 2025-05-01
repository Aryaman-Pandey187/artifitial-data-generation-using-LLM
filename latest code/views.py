from django.shortcuts import render, redirect
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

import threading

import logging
logging.basicConfig(level=logging.INFO)


from django.db import models

from django.utils.dateparse import parse_datetime
from django.db.models import Q

class Log(models.Model):
    session_id = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    retrieved = models.BooleanField(default=False)  # New field

def store_log(request, message):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()  # Create a session if it doesn't exist
        session_id = request.session.session_key
    Log.objects.create(session_id=session_id, message=message)

def fetch_logs(request):
    session_id = request.session.session_key
    logs = Log.objects.filter(session_id=session_id, retrieved=False).order_by('timestamp')

    # Serialize logs
    log_data = [{'timestamp': log.timestamp, 'message': log.message} for log in logs]

    # Mark logs as retrieved
    logs.update(retrieved=True)

    return JsonResponse({'logs': log_data})

def login_view(request):
    request.session.cycle_key()
    if request.method == 'POST':
        # Retrieve the form data
        intranetID = request.POST.get('intranetID')
        password = request.POST.get('password')

        # Check if both fields are filled
        if intranetID and password:
            # Store the values in the session
            request.session['intranetID'] = intranetID
            request.session['password'] = password

            user = True
            # time.sleep(3)

            if user == True:
                return redirect('source_info_page')
            else:
                return render(request, 'auth_app/login.html', {'invalid_credentials': True})

            # Redirect to the source info page
            return redirect('source_info_page')
            
        else:
            # Return the form with an error if fields are missing
            return render(request, 'auth_app/login.html', {'error': 'Please fill in both fields'})

    return render(request, 'auth_app/login.html')


# def authenticate_with_selenium(intranetID, password):
#     # Configure Selenium
#     options = Options()
#     options.add_argument('--headless')  # Run in headless mode for production
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')

#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

#     try:
#         # Replace with the target website URL
#         target_url = 'https://example.com/login'
#         driver.get(target_url)

#         # Locate input fields and enter credentials (adjust locators as needed)
#         driver.find_element(By.ID, 'username').send_keys(intranetID)
#         driver.find_element(By.ID, 'password').send_keys(password, Keys.RETURN)

#         time.sleep(2)  # Wait for the page to load

#         # Check for a successful login (adjust logic based on the site)
#         if "Welcome" in driver.page_source:
#             return True
#         return False
#     except Exception as e:
#         print(f"Error during Selenium authentication: {e}")
#         return False
#     finally:
#         driver.quit()

# Render the source information page
def source_info_page(request):
    intranetID = request.session.get('intranetID')
    password = request.session.get('password')

    if request.method == 'POST':
        source_database = request.POST.get('source_database')
        source_table = request.POST.get('source_table')

        request.session['intranetID'] = intranetID
        request.session['password'] = password

        request.session['source_database'] = source_database
        request.session['source_table'] = source_table

        print(f"Intranet ID: {intranetID}, Password: {password}")
        print(f"Source Database: {source_database}, Source Table: {source_table}")

        # Check if credentials are available
        if source_table and source_database:
            return redirect('target_env_page')  # Redirect back to login if session data is missing

    return render(request, 'auth_app/source_info.html')

def target_env_page(request):
    intranetID = request.session.get('intranetID')
    password = request.session.get('password')
    source_database = request.session.get('source_database')
    source_table = request.session.get('source_table')

    if request.method == 'POST':
        target_env_name = request.POST.get('target_env_name')

        request.session['target_env_name'] = target_env_name

        print(f"Intranet ID: {intranetID}, Password: {password}")
        print(f"Source Database: {source_database}, Source Table: {source_table}")
        print(f"radio-button-choice: {target_env_name}")

        if target_env_name:
            return redirect('target_env_login')

    return render(request, 'auth_app/target_env_page.html')

def target_env_login(request):
    intranetID = request.session.get('intranetID')
    password = request.session.get('password')
    source_database = request.session.get('source_database')
    source_table = request.session.get('source_table')
    target_env_name = request.session.get('target_env_name')

    if request.method == 'POST':
        target_env_username = request.POST.get('target_env_username')
        target_env_password = request.POST.get('target_env_password')

        request.session['target_env_username'] = target_env_username
        request.session['target_env_password'] = target_env_password

        print(f"Intranet ID: {intranetID}, Password: {password}")
        print(f"Source Database: {source_database}, Source Table: {source_table}")
        print(f"radio-button-choice: {target_env_name}")
        print(f"Target Env Username: {target_env_username}, Target Env Password: {target_env_password}")

        # return redirect(target_info_page)
        return redirect('target_info_page')

    return render(request, 'auth_app/target_env_login.html', {'message': target_env_name})

def target_info_page(request):
    intranetID = request.session.get('intranetID')
    password = request.session.get('password')
    source_database = request.session.get('source_database')
    source_table = request.session.get('source_table')
    target_env_name = request.session.get('target_env_name')
    target_env_username = request.session.get('target_env_username')
    target_env_password = request.session.get('target_env_password')

    if request.method == 'POST':
        target_database = request.POST.get('target_database')
        target_table = request.POST.get('target_table')

        request.session['target_database'] = target_database
        request.session['target_table'] = target_table

        print(f"Intranet ID: {intranetID}, Password: {password}")
        print(f"Source Database: {source_database}, Source Table: {source_table}")
        print(f"radio-button-choice: {target_env_name}")
        print(f"Target Env Username: {target_env_username}, Target Env Password: {target_env_password}")
        print(f"Target Database: {target_database}, Target Table: {target_table}")

        return redirect('details_verification_page_with_logging')

    return render(request, 'auth_app/target_info_page.html')

# Mock verification functions (Replace with actual implementations)
def verify_prod_login(request):
    # Simulate processing
    import time
    time.sleep(1)  # Simulate delay
    store_log(request, "INFO: PROD Login verified successfully.")
    # return True, "PROD Login verified successfully."

def verify_if_user_has_access_to_prod_database(request):
    import time
    time.sleep(1)  # Simulate delay
    store_log(request, "INFO: User has access to PROD database.")
    # return True, "User has access to PROD database."

def verify_target_env_access(request):
    import time
    time.sleep(1)  # Simulate delay
    store_log(request, "INFO: Target ENV access verification failed.")
    # return False, "Target ENV access verification failed."

def verify_if_user_has_access_to_target_ENV_database(request):
    import time
    time.sleep(1)  # Simulate delay
    store_log(request, "INFO: User has access to target ENV database.")
    # return True, "User has access to target ENV database."

def verify_if_target_and_source_table_have_same_schema(request):
    import time
    time.sleep(1)  # Simulate delay
    store_log(request, "INFO: Target and source tables have the same schema.")
    # return True, "Target and source tables have the same schema."

# Map function names to actual implementations
# function_mapping = {
#     "verify_prod_login": verify_prod_login,
#     "verify_if_user_has_access_to_prod_database": verify_if_user_has_access_to_prod_database,
#     "verify_target_env_access": verify_target_env_access,
#     "verify_if_user_has_access_to_target_ENV_database": verify_if_user_has_access_to_target_ENV_database,
#     "verify_if_target_and_source_table_have_same_schema": verify_if_target_and_source_table_have_same_schema,
# }

# # AJAX endpoint to run backend functions
# def run_function(request):
#     if request.method == "POST":
#         function_name = request.POST.get("function_name")
#         if function_name in function_mapping:
#             success, message = function_mapping[function_name](request)
#             if success:
#                 return JsonResponse({"message": message})
#             else:
#                 return JsonResponse({"message": message}, status=400)
#         return JsonResponse({"message": "Invalid function name."}, status=400)
#     return JsonResponse({"message": "Invalid request method."}, status=405)



def details_verification_page_with_logging(request):
    print("SESSION ID: " + str(request.session.session_key))
    threading.Thread(target=details_verification_tasks, args=(request,)).start()

    return render(request, 'auth_app/details_verification_page_with_logging.html')

def details_verification_tasks(request):
    verify_prod_login(request)
    verify_if_user_has_access_to_prod_database(request)
    verify_target_env_access(request)
    verify_if_user_has_access_to_target_ENV_database(request)
    verify_if_target_and_source_table_have_same_schema(request)

    # request.session['tasks_complete'] = True
    # print("Tasks complete flag set for session:", request.session.session_key)
    # print("Tasks complete flag set for session:", request.session['tasks_complete'])


def check_tasks_complete(request):
    tasks_complete = request.session.get('tasks_complete', True)

    # Clear the flag after checking to avoid repeated redirects
    # if tasks_complete:
    #     del request.session['tasks_complete']

    return JsonResponse({'tasks_complete': tasks_complete})

def last_page(request):
    return render(request, 'auth_app/last_page.html')  # Replace with your desired template

# delete all DB data once all required data is inserted into the DB.
def clear_session_data(request):
    request.session.flush()  # Clears all session data
    return redirect('login')  # Redirect to the desired page




# ****************               WORK TO DO -  
# Once some logs are displayed, I dont want the same to displayed again in the next fetch, - har log ke sath ek ID attatch krr do
# then ID ke basis pe next time retrieve kroo 
# how to deploy django code in production
# use docker with django




# what if any verification failes on the 