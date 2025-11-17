"""
Script Variation Generator Module
Generates variations of scripts using AI (OpenAI GPT)
"""

import os
import json
from openai import OpenAI
import config

class ScriptVariationGenerator:
    def __init__(self):
        """Initialize Script Variation Generator"""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.variations_dir = config.VARIATIONS_DIR
        os.makedirs(self.variations_dir, exist_ok=True)

    def generate_variations(self, original_script, num_variations=3, persona_variations=None):
        """
        Generate variations of the original script

        Args:
            original_script (str): Original video script
            num_variations (int): Number of variations to generate
            persona_variations (list): Optional list of persona descriptions

        Returns:
            list: List of script variations
        """
        variations = []

        # Default personas if none provided
        if persona_variations is None:
            persona_variations = [
                "enthusiastic and energetic reviewer who uses casual language",
                "professional and detailed expert who focuses on technical aspects",
                "friendly and relatable person who shares personal experiences",
                "skeptical but fair critic who points out both pros and cons",
                "knowledgeable influencer who compares products with alternatives",
            ]

        for i in range(num_variations):
            persona = persona_variations[i % len(persona_variations)]
            variation = self._generate_single_variation(original_script, persona, i + 1)
            variations.append(variation)

        return variations

    def _generate_single_variation(self, original_script, persona, variation_number):
        """
        Generate a single script variation

        Args:
            original_script (str): Original script text
            persona (str): Persona description
            variation_number (int): Variation number

        Returns:
            dict: Variation data
        """
        print(f"Generating variation {variation_number} with persona: {persona}")

        prompt = f"""You are creating a variation of a product review video script.

Original Script:
{original_script}

Create a NEW version of this review with the following persona:
{persona}

Requirements:
1. Keep the same product and key points
2. Change the delivery style, word choice, and examples
3. Adjust the tone to match the persona
4. Keep roughly the same length
5. Make it feel like a completely different person
6. Include natural speech patterns and filler words appropriate for the persona
7. DO NOT copy phrases directly from the original

Write ONLY the new script, no explanations or meta-commentary:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a creative scriptwriter who specializes in creating authentic-sounding product review variations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Higher temperature for more creativity
            )

            variation_text = response.choices[0].message.content

            variation_data = {
                'variation_number': variation_number,
                'persona': persona,
                'script': variation_text,
                'word_count': len(variation_text.split()),
            }

            print(f"✓ Variation {variation_number} generated ({variation_data['word_count']} words)")

            return variation_data

        except Exception as e:
            print(f"✗ Error generating variation {variation_number}: {str(e)}")
            raise

    def save_variations(self, variations, base_filename):
        """
        Save variations to files

        Args:
            variations (list): List of variation data
            base_filename (str): Base filename for saving

        Returns:
            list: List of saved file paths
        """
        saved_paths = []

        # Save all variations in one JSON file
        json_path = os.path.join(self.variations_dir, f"{base_filename}_variations.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(variations, f, indent=2, ensure_ascii=False)
        saved_paths.append(json_path)
        print(f"✓ All variations saved: {json_path}")

        # Save individual text files
        for i, variation in enumerate(variations, 1):
            txt_path = os.path.join(self.variations_dir, f"{base_filename}_variation_{i}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Persona: {variation['persona']}\n")
                f.write(f"{'='*60}\n\n")
                f.write(variation['script'])
            saved_paths.append(txt_path)
            print(f"✓ Variation {i} saved: {txt_path}")

        return saved_paths

    def generate_custom_variation(self, original_script, custom_instructions):
        """
        Generate a variation with custom instructions

        Args:
            original_script (str): Original script
            custom_instructions (str): Custom modification instructions

        Returns:
            str: Generated variation
        """
        prompt = f"""Modify the following script based on these instructions:

Instructions: {custom_instructions}

Original Script:
{original_script}

Write the modified script:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a scriptwriter who modifies scripts based on user instructions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"✗ Error generating custom variation: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    generator = ScriptVariationGenerator()
    print("Script variation generator ready!")
    print(f"Variations directory: {generator.variations_dir}")
