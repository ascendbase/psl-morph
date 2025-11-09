import requests
import os
from dotenv import load_dotenv
import math

load_dotenv()  # Load environment variables from .env file

class BetafaceClient:
    def __init__(self, api_key=None, api_secret=None):
        # For Betaface API v2, api_key is required in form data; api_secret is not needed for v2
        # Use the free tier api_key if not provided
        self.api_key = api_key if api_key else os.getenv("BETAFACE_API_KEY") or "d45fd466-51e2-4701-8da8-04351c872236"
        self.api_secret = api_secret if api_secret else os.getenv("BETAFACE_API_SECRET")  # Not used in v2, but kept for compatibility
        self.base_url = "https://www.betafaceapi.com/api/v2/"

    def _call_api(self, endpoint, method="POST", data=None, files=None, json_payload=None):
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'} if json_payload else {}
        try:
            if method == "POST":
                if json_payload:
                    response = requests.post(url, json=json_payload, headers=headers)
                elif files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, data=data, headers=headers)
            elif method == "GET":
                response = requests.get(url, params=data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            print(f"Response content: {e.response.text if e.response else 'N/A'}")
            return None

    def upload_and_analyze_image(self, image_path):
        """
        Uploads an image file to Betaface API using the /media/file endpoint
        and returns the analysis result directly.
        """
        try:
            with open(image_path, 'rb') as f:
                # Use 'file' as the field name per API spec
                files = {'file': (os.path.basename(image_path), f)}
                # Include api_key and detection_flags in form data
                # detection_flags to enable propoints for detailed landmarks, classifiers for attributes, etc.
                data = {
                    'api_key': self.api_key,
                    'detection_flags': 'basicpoints,propoints,classifiers,extended,content'  # Enable detailed detection and landmarks
                }
                response = self._call_api("media/file", method="POST", files=files, data=data)
                
                if response and 'media' in response and 'faces' in response['media'] and response['media']['faces']:
                    # Assuming single face for simplicity
                    return response['media']['faces'][0]
                else:
                    error_msg = response.get('error', {}).get('message', 'Unknown error') if response else 'No response'
                    print(f"Image upload and analysis failed for {image_path}: {error_msg}")
                    return None
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return None
        except Exception as e:
            print(f"Error uploading and analyzing image: {e}")
            return None

    def get_facial_landmarks_data(self, analysis_result):
        """
        Retrieves detailed facial landmark data from an analysis result.
        Converts list of points to a dict keyed by name for easier access.
        """
        if analysis_result and "points" in analysis_result:
            # Betaface returns 'points' as list of dicts with 'name', 'x', 'y'
            # Normalize names for easier lookup
            landmarks_dict = {}
            for p in analysis_result['points']:
                name = p['name'].lower().replace('_', ' ')
                landmarks_dict[name] = {'x': p['x'], 'y': p['y']}
            return landmarks_dict
        return None

    def get_shape_diff(self, landmarks1, landmarks2, feature):
        """
        Calculates shape differences between two sets of facial landmarks for a specific feature.
        Uses actual Betaface landmark names (e.g., 'eye left', 'eye right', etc.).
        Implements basic calculations; extend as needed.
        """
        if not landmarks1 or not landmarks2:
            return "N/A (missing landmarks)"

        try:
            if feature == 'eye':
                # Try to compute width using left and right eye outer corners
                left_keys = [k for k in landmarks1.keys() if 'eye left' in k and 'outer' in k or 'corner' in k]
                right_keys = [k for k in landmarks1.keys() if 'eye right' in k and ('outer' in k or 'corner' in k)]
                if left_keys and right_keys:
                    lk, rk = left_keys[0], right_keys[0]
                    width1 = math.dist([landmarks1[lk]['x'], landmarks1[lk]['y']],
                                       [landmarks1[rk]['x'], landmarks1[rk]['y']])
                    width2 = math.dist([landmarks2[lk]['x'], landmarks2[lk]['y']],
                                       [landmarks2[rk]['x'], landmarks2[rk]['y']])
                    return (width2 - width1) / width1 * 100 if width1 else 0
                return "N/A (eye landmarks not found)"
            elif feature == 'nose':
                nose_keys = [k for k in landmarks1.keys() if 'nose' in k]
                if len(nose_keys) >= 2:
                    # Pick min y as top, max y as bottom
                    top1 = min(landmarks1[k]['y'] for k in nose_keys)
                    bot1 = max(landmarks1[k]['y'] for k in nose_keys)
                    top2 = min(landmarks2[k]['y'] for k in nose_keys if k in landmarks2)
                    bot2 = max(landmarks2[k]['y'] for k in nose_keys if k in landmarks2)
                    return (bot2 - top2 - (bot1 - top1)) / (bot1 - top1) * 100 if (bot1 - top1) else 0
                return "N/A (nose landmarks not found)"
            elif feature == 'jaw':
                if 'face contour left' in landmarks1 and 'face contour right' in landmarks1:
                    width1 = math.dist([landmarks1['face contour left']['x'], landmarks1['face contour left']['y']],
                                       [landmarks1['face contour right']['x'], landmarks1['face contour right']['y']])
                    width2 = math.dist([landmarks2['face contour left']['x'], landmarks2['face contour left']['y']],
                                       [landmarks2['face contour right']['x'], landmarks2['face contour right']['y']])
                    return (width2 - width1) / width1 * 100 if width1 else 0
                return "N/A (jaw landmarks not found)"
            elif feature == 'lips':
                if 'mouth left corner' in landmarks1 and 'mouth right corner' in landmarks1:
                    width1 = math.dist([landmarks1['mouth left corner']['x'], landmarks1['mouth left corner']['y']],
                                       [landmarks1['mouth right corner']['x'], landmarks1['mouth right corner']['y']])
                    width2 = math.dist([landmarks2['mouth left corner']['x'], landmarks2['mouth left corner']['y']],
                                       [landmarks2['mouth right corner']['x'], landmarks2['mouth right corner']['y']])
                    return (width2 - width1) / width1 * 100 if width1 else 0
                return "N/A (lips landmarks not found)"
            elif feature == 'skull':
                if 'temple left' in landmarks1 and 'temple right' in landmarks1:
                    width1 = math.dist([landmarks1['temple left']['x'], landmarks1['temple left']['y']],
                                       [landmarks1['temple right']['x'], landmarks1['temple right']['y']])
                    width2 = math.dist([landmarks2['temple left']['x'], landmarks2['temple left']['y']],
                                       [landmarks2['temple right']['x'], landmarks2['temple right']['y']])
                    return (width2 - width1) / width1 * 100 if width1 else 0
                return "N/A (skull landmarks not found)"
            return "N/A (feature not implemented)"
        except KeyError as e:
            print(f"Warning: Landmark not found for feature '{feature}': {e}")
            return "N/A (landmark missing)"

if __name__ == "__main__":
    # Example Usage:
    # Set BETAFACE_API_KEY in .env if using custom; defaults to free tier

    original_image_path = "betaface_test_images/original.png"
    morphed_image_path = "betaface_test_images/morphed.png"

    os.makedirs(os.path.dirname(original_image_path), exist_ok=True)

    if not os.path.exists(original_image_path):
        print(f"Error: Original image not found at {original_image_path}")
        exit()
    if not os.path.exists(morphed_image_path):
        print(f"Error: Morphed image not found at {morphed_image_path}")
        exit()

    try:
        client = BetafaceClient()

        print(f"Uploading and analyzing original image: {original_image_path}")
        analysis1 = client.upload_and_analyze_image(original_image_path)
        
        print(f"Uploading and analyzing morphed image: {morphed_image_path}")
        analysis2 = client.upload_and_analyze_image(morphed_image_path)

        if analysis1 and analysis2:
            landmarks1 = client.get_facial_landmarks_data(analysis1)
            landmarks2 = client.get_facial_landmarks_data(analysis2)

            if landmarks1 and landmarks2:
                eye_diff = client.get_shape_diff(landmarks1, landmarks2, 'eye')
                nose_diff = client.get_shape_diff(landmarks1, landmarks2, 'nose')
                jaw_diff = client.get_shape_diff(landmarks1, landmarks2, 'jaw')
                lips_diff = client.get_shape_diff(landmarks1, landmarks2, 'lips')
                skull_diff = client.get_shape_diff(landmarks1, landmarks2, 'skull')

                # Custom Output: Format as table
                # Note: 'Before' and 'After' placeholders; in real use, compute actual shapes (e.g., ratios)
                import pandas as pd
                data = {
                    'Feature': ['Eye Shape', 'Nose Shape', 'Jaw Shape', 'Lips Shape', 'Skull Shape'],
                    'Before': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],  # Replace with computed values from landmarks1
                    'After': ['N/A', 'N/A', 'N/A', 'N/A', 'N/A'],   # Replace with computed values from landmarks2
                    'Difference': [
                        f'{eye_diff:.2f}% change' if isinstance(eye_diff, (int, float)) else eye_diff,
                        f'{nose_diff:.2f}% change' if isinstance(nose_diff, (int, float)) else nose_diff,
                        f'{jaw_diff:.2f}% change' if isinstance(jaw_diff, (int, float)) else jaw_diff,
                        f'{lips_diff:.2f}% change' if isinstance(lips_diff, (int, float)) else lips_diff,
                        f'{skull_diff:.2f}% change' if isinstance(skull_diff, (int, float)) else skull_diff
                    ]
                }
                df = pd.DataFrame(data)
                print("\nFacial Feature Differences:")
                print(df.to_markdown(index=False))
            else:
                print("Could not retrieve facial landmarks from one or both analysis results.")
        else:
            print("Failed to analyze one or both images. Ensure images contain detectable faces and API key is valid.")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        pass
