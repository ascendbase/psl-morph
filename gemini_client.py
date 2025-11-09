import os
import base64
import requests
import json
from PIL import Image
import io
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key=GEMINI_API_KEY):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
        self.headers = {
            "Content-Type": "application/json",
        }
        if not self.api_key:
            logger.error("GEMINI_API_KEY is not set in config.py or environment variables.")
            raise ValueError("GEMINI_API_KEY is required for GeminiClient.")

    def _encode_image_to_base64(self, image_path):
        """Encodes an image file to a base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return None
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None

    def analyze_facial_features(self, original_image_path, morphed_image_path, system_prompt_text):
        """
        Analyzes facial features between two images using the Gemini Pro Vision model.

        Args:
            original_image_path (str): Path to the original image.
            morphed_image_path (str): Path to the morphed image.
            system_prompt_text (str): The system prompt to guide the AI's analysis.

        Returns:
            dict: A dictionary containing the analysis result, or None if an error occurs.
        """
        original_image_base64 = self._encode_image_to_base64(original_image_path)
        morphed_image_base64 = self._encode_image_to_base64(morphed_image_path)

        if not original_image_base64 or not morphed_image_base64:
            return {"error": "Failed to encode one or both images to base64."}

        # Construct the prompt with the system prompt and image data
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt_text},
                        {"inline_data": {"mime_type": "image/jpeg", "data": original_image_base64}},
                        {"text": "Image 1: Original"},
                        {"inline_data": {"mime_type": "image/jpeg", "data": morphed_image_base64}},
                        {"text": "Image 2: Morphed"},
                        {"text": "Please compare the two images based on the provided facial features and output the differences directly related to these facial features and their according mentioned relevant parameters. This list of facial features is organized in order of importance. You need to evaluate the amount of differences based on these facial features and their relative importance to output the list of differences based on this evaluation, for example -> facial leanness feature difference is 4/10 and importance is 8/8 = 32 score of relative importance. then list all features based on these individual relative importance scores (from highest to lowest score)."}
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=300 # 5 minutes timeout
            )
            response.raise_for_status() # Raise an exception for HTTP errors

            response_data = response.json()
            if "candidates" in response_data and response_data["candidates"]:
                # Assuming the first candidate's text is the analysis
                analysis_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                return {"analysis": analysis_text}
            else:
                logger.warning(f"Gemini API response did not contain candidates: {response_data}")
                return {"error": "Gemini API did not return a valid analysis."}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {"error": f"Error communicating with Gemini API: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding Gemini API response: {e}")
            return {"error": "Invalid response from Gemini API."}
        except Exception as e:
            logger.error(f"An unexpected error occurred during Gemini analysis: {e}")
            return {"error": f"An unexpected error occurred: {e}"}

if __name__ == '__main__':
    # This block is for testing the GeminiClient directly
    # You would typically set GEMINI_API_KEY in your environment variables
    # For testing, you can temporarily set it here:
    # os.environ['GEMINI_API_KEY'] = 'YOUR_GEMINI_API_KEY'

    # Create dummy image files for testing
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple original image
        img_original = Image.new('RGB', (200, 200), color = 'red')
        draw_original = ImageDraw.Draw(img_original)
        draw_original.ellipse((50, 50, 150, 150), fill='blue')
        img_original.save('test_original.jpg')

        # Create a simple morphed image (slightly different)
        img_morphed = Image.new('RGB', (200, 200), color = 'red')
        draw_morphed = ImageDraw.Draw(img_morphed)
        draw_morphed.ellipse((40, 40, 160, 160), fill='green')
        img_morphed.save('test_morphed.jpg')

        print("Created dummy images: test_original.jpg and test_morphed.jpg")

        client = GeminiClient()
        
        # Example system prompt (this would come from the database in the app)
        test_system_prompt = """
        You are an expert facial features analyst. Your task is to compare two images of a face, one original and one morphed, and identify the differences in facial features based on the following criteria. For each feature, evaluate the "amount of difference" on a scale of 1-10 (1 being almost no difference, 10 being a very significant difference). Then, multiply this difference score by the "importance" score (provided in parentheses next to each feature). Finally, list all features based on these individual relative importance scores, from highest to lowest.

        Facial Features and their Importance:
        1. Facial leanness (Importance = 8): Appearance of “tight” facial skin without any visible facial fat sagging. Shows the underlying bone structure, increases perceived facial depth via various shadows under various lighting. The desired appearance depends not only on the obvious total low body fat % levels but on the underlying bone morphology AND certain soft tissues (SMAS) morphology.
        2. Facial Width (Importance = 7): Both bizygomatic (cheekbones) and bigonial (jaw)
        3. Eyes (Importance = 6): I'm talking about the eyes morphology separately from the eyebrows appearance here. The specific relevant parameters here are: deep set, compact (smaller and more almond shaped) or bigger (rounder) and wide eyes (high PFL, low PFH) or rounder (low PFL).
        4. Nose (Importance = 5): nose tip width and bulbosity instead of narrower or more refined, sharper nose tip, symmetry, nose tip rotation (tip and nostrils pointring downward or upwards)
        5. Health Indicators (Importance = 4): Clear, homogenous (even) skin texture without wrinkles, acne scars, signs of skin aging or other skin imperfections. Symmetrical facial features like hairline, temporal bones, eyebrows, eyes (+ eye focus (no amblyopia)), nose bridge and tip, lips, chin, cheekbones, and mandible alignment. Straight hairline without balding patterns.
        6. Mouth and Lips (Importance = 3): mouth width and lips volume (both upper lip and lower lip, and their volumes ratio)
        7. Facial Angularity (Importance = 2): I'm talking specifically about the contour of the face here. Not the general facial leanness, but certain facial bones spots angularity. Angularity spots: temporal cave in, cheekbones outwards, ramus cave in, gonions outwards, mandible cave in, chin outwards (square).
        8. Eyebrows (Importance = 1): Wide (visible inner and outer corners eyebrows region), thick, closet set (vertically) eyebrows.
        """
        
        print("\nAnalyzing facial features...")
        analysis_result = client.analyze_facial_features('test_original.jpg', 'test_morphed.jpg', test_system_prompt)
        
        if "analysis" in analysis_result:
            print("\nAnalysis Result:")
            print(analysis_result["analysis"])
        else:
            print(f"Error: {analysis_result.get('error', 'Unknown error')}")

    except ImportError:
        print("Pillow library not found. Please install it (`pip install Pillow`) to run the test block.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        # Clean up dummy images
        if os.path.exists('test_original.jpg'):
            os.remove('test_original.jpg')
        if os.path.exists('test_morphed.jpg'):
            os.remove('test_morphed.jpg')
