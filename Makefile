# TODO 
install:
	pip install -r requirements.txt
	pip install pytubex
	yarn

upload:
	python upload.py

uiupload:
	python upload_through_ui.py

public:
	python set_draft_video_public_with_metadata.py