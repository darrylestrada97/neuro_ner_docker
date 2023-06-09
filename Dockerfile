# Use an official python image
FROM python:3.5

# Set the working directory to /app
WORKDIR /app

# COPY tensorflow-2.5.0-cp38-cp38-linux_x86_64.whl .
# copy the dependencies file to the working directory
COPY requirements.txt .

# RUN pip3 install -U tensorflow-2.5.0-cp38-cp38-linux_x86_64.whl
# install dependencies
#
RUN git clone https://github.com/TeMU-BSC/PharmaCoNER-Tagger.git
RUN pip install -r requirements.txt
RUN python -m spacy download es

#RUN python -m spacy download es_core_news_sm

# Copy the current directory contents into the container at /app 
COPY . /app
WORKDIR /app
# cmd for uwsgi server 
CMD [ "uwsgi","--http","0.0.0.0:5000","--callable", "app","--module","app","--master","--processes", "4", "--threads","2"] 


# Copy necessary files for "nltk" python package into one of these directories inside container:
#   - '/root/nltk_data'
#   - '/usr/local/nltk_data'
#   - '/usr/local/share/nltk_data'
#   - '/usr/local/lib/nltk_data'
#   - '/usr/share/nltk_data'
#   - '/usr/local/share/nltk_data'
#   - '/usr/lib/nltk_data'
#   - '/usr/local/lib/nltk_data'
#   - ''
# COPY nltk_data /usr/local/nltk_data