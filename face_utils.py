import os
import face_recognition


def save_face(img_file, username):
    """
    Save user's face image.
    """
    os.makedirs("faces", exist_ok=True)

    img_path = os.path.join("faces", f"{username}.jpg")

    with open(img_path, "wb") as f:
        f.write(img_file.getbuffer())

    return img_path


def verify_faces(stored_path, live_image_path):
    """
    Compare stored face with live captured face.
    Returns True if matched, otherwise False.
    """

    if not os.path.exists(stored_path):
        return False

    if not os.path.exists(live_image_path):
        return False

    try:
        stored_img = face_recognition.load_image_file(stored_path)
        live_img = face_recognition.load_image_file(live_image_path)

        stored_encoding = face_recognition.face_encodings(stored_img)
        live_encoding = face_recognition.face_encodings(live_img)

        if len(stored_encoding) == 0:
            return False

        if len(live_encoding) == 0:
            return False

        result = face_recognition.compare_faces(
            [stored_encoding[0]],
            live_encoding[0],
            tolerance=0.5
        )

        return result[0]

    except Exception as e:
        print("Face Error:", e)
        return False