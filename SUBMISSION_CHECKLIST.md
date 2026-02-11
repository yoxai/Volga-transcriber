# Assessment Submission Checklist

## 1. Source Code (Git Repo)

The assessment requires you to "share the source code in a GIT repo".

1. Initialize a git repo in this folder: `git init`
2. Add all files: `git add .`
3. Commit: `git commit -m "Initial commit of audio transcription pipeline"`
4. Create a public/private repository (GitHub/GitLab).
5. Push your code:

    ```bash
    git remote add origin <your-repo-url>
    git push -u origin main
    ```

6. **Copy the Repo URL** for the form.

## 2. Video Recording

The assessment requires a "short video explaining how the code works".

1. Use a screen recorder (e.g., Loom, OBS).
2. **Script Outline**:
    - **Intro**: "Hi, I'm [Name]. This is my transcription pipeline."
    - **Demo**:
        - Show `python api.py` running in terminal.
        - Open `http://localhost:8000/docs`.
        - Upload an audio file.
        - Show the JSON response with timestamps.
    - **Code Walkthrough**:
        - Point to `transcription_service.py` (chunking logic).
        - Point to `README.md` (System Design answers).
    - **Closing**: "Thanks."
3. Upload/Attach the video.

## 3. Documents

- [x] **README.md**: Contains "System Design Answers" (Part 2).
- [ ] **Resume/CV**: Don't forget to attach if required.
