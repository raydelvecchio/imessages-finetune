from openai import OpenAI
from preprocess import TUNE_FILE

client = OpenAI()

def upload_training_file(file_path: str = TUNE_FILE) -> str:
    """
    Upload a training file to OpenAI. This is our .jsonl of the imessage fine tune.
    """
    with open(file_path, "rb") as file:
        response = client.files.create(
            file=file,
            purpose="fine-tune"
        )
    return response.id

def create_fine_tuning_job(file_id: str, model: str = "gpt-4o") -> str:
    """
    Create a fine-tuning job. Returns the ID of the fine tuning job.
    """
    response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model
    )
    print(f"FINE TUNING JOB ID: {response.id}")
    return response.id

def check_fine_tuning_status(job_id: str) -> str:
    """
    Check the status of a fine-tuning job.
    
    Args:
    job_id (str): The ID of the fine-tuning job
    
    Returns:
    str: The status of the fine-tuning job
    """
    response = client.fine_tuning.jobs.retrieve(job_id)
    return response.status

def use_fine_tuned_model(model: str, messages: list) -> str:
    """
    Use the fine-tuned model to generate a response.
    
    Args:
    model (str): The name of the fine-tuned model
    messages (list): A list of message dictionaries
    
    Returns:
    str: The generated response
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    file_id = upload_training_file()
    print(f"File uploaded with ID: {file_id}")

    job_id = create_fine_tuning_job(file_id)
    print(f"Fine-tuning job created with ID: {job_id}")

    status = check_fine_tuning_status(job_id)
    print(f"Fine-tuning job {job_id} status: {status}")
