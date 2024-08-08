from flask import Flask, render_template, request, redirect, url_for
import requests
import tempfile
import os

app = Flask(__name__)

def process_document(api_url, prompt_id, prompt_text, file_path, save_prompt_flag, access_token):
    try:
        endpoint_url = f"{api_url}/process-document"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        files = {
            'file': open(file_path, 'rb')
        }
        data = {
            'prompt_id': prompt_id,
            'prompt_text': prompt_text,
            'save_prompt_flag': save_prompt_flag
        }
        response = requests.post(endpoint_url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error: {response.status_code} - {response.text}"}
    except requests.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'clear' in request.form:
            return redirect(url_for('index'))

        api_url = "http://20.84.101.4:8080"
        prompt_id = request.form.get('prompt_id')
        prompt_text = request.form.get('prompt_text', '')
        file = request.files.get('file')
        save_prompt_flag = request.form.get('save_prompt_flag', 'false') == 'true'
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyMzEwOTY4M30.x5457zjSwnDGcQljY0IHQ5V7RAIf7Mekol1S2jGCZVE"

        file_name = file.filename if file else None

        # Check if a file is uploaded
        if not file:
            return render_template('index.html', prompt_id=prompt_id, prompt_text=prompt_text, save_prompt_flag=save_prompt_flag, file_name=file_name, error="File is required")

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file_path = temp_file.name
                file.save(file_path)
        except Exception as e:
            return render_template('index.html', prompt_id=prompt_id, prompt_text=prompt_text, save_prompt_flag=save_prompt_flag, file_name=file_name, error=f"Failed to save the file: {str(e)}")

        try:
            response = process_document(api_url, prompt_id, prompt_text, file_path, save_prompt_flag, access_token)
        except Exception as e:
            return render_template('index.html', prompt_id=prompt_id, prompt_text=prompt_text, save_prompt_flag=save_prompt_flag, file_name=file_name, error=f"Failed to process the document: {str(e)}")
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)

        return render_template('index.html', response=response, prompt_id=prompt_id, prompt_text=prompt_text, save_prompt_flag=save_prompt_flag, file_name=file_name)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
