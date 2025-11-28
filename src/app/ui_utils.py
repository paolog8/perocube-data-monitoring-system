def get_delete_warning_html(item_name):
    """
    Returns a styled HTML string for delete confirmation warning.
    """
    return f"""
    <div style="
        background-color: #ffebee; 
        border: 1px solid #ffcdd2; 
        padding: 15px; 
        border-radius: 5px; 
        color: #b71c1c; 
        margin-bottom: 20px;
        font-family: sans-serif;
    ">
        <strong>⚠️ Warning:</strong> Are you sure you want to delete '<b>{item_name}</b>'? 
        <br>
        This action cannot be undone.
    </div>
    """
