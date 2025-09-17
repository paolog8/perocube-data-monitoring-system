# Use the official Jupyter image as a base
FROM jupyter/datascience-notebook:latest

# Switch to the root user to install packages
USER root

# Install the required Python packages
RUN pip install voila ipywidgets

# Switch back to the default jovyan user
USER jovyan
