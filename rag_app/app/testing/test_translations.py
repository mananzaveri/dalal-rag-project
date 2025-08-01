import sys
import os
import time
import itertools
from datetime import datetime
import pandas as pd

# Add your project path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.backend.translator.translator import translate
from app.backend.core.retriever import RAGRetriever


class TranslationTester:
    def __init__(self):
        self.languages = [
            "English", "Spanish", "French", "Russian",
            "Hindi", "Gujarati", "Chinese (Simplified)", "Thai"
        ]

        # Buddhism-specific questions
        self.test_questions = {
            "English": [
                "Who was Siddhartha Gautama and why is he important in Buddhism?",
                "What are the Four Noble Truths?",
                "Explain the concept of Nirvana in Buddhism.",
                "What is the significance of meditation in Buddhist practice?",
                "Describe the difference between Mahayana and Theravada Buddhism."
            ],
            "Spanish": [
                "¿Quién fue Siddhartha Gautama y por qué es importante en el budismo?",
                "¿Cuáles son las Cuatro Nobles Verdades?",
                "Explica el concepto de Nirvana en el budismo.",
                "¿Cuál es la importancia de la meditación en la práctica budista?",
                "Describe la diferencia entre el budismo Mahayana y Theravada."
            ],
            "French": [
                "Qui était Siddhartha Gautama et pourquoi est-il important dans le bouddhisme?",
                "Quelles sont les Quatre Nobles Vérités?",
                "Expliquez le concept de Nirvana dans le bouddhisme.",
                "Quelle est l'importance de la méditation dans la pratique bouddhiste?",
                "Décrivez la différence entre le bouddhisme Mahayana et Theravada."
            ],
            "Russian": [
                "Кем был Сиддхартха Гаутама и почему он важен в буддизме?",
                "Каковы Четыре Благородные Истины?",
                "Объясните концепцию Нирваны в буддизме.",
                "Каково значение медитации в буддийской практике?",
                "Опишите разницу между махаяной и тхеравадой в буддизме."
            ],
            "Hindi": [
                "सिद्धार्थ गौतम कौन थे और बौद्ध धर्म में वे क्यों महत्वपूर्ण हैं?",
                "चार आर्य सत्य क्या हैं?",
                "बौद्ध धर्म में निर्वाण की अवधारणा को समझाइए।",
                "बौद्ध अभ्यास में ध्यान का क्या महत्व है?",
                "महायान और थेरवाद बौद्ध धर्म में क्या अंतर है?"
            ],
            "Gujarati": [
                "સિદ્ધાર્થ ગૌતમ કોણ હતા અને બૌદ્ધ ધર્મમાં તેઓ શા માટે મહત્વપૂર્ણ છે?",
                "ચાર આર્ય સત્ય શું છે?",
                "બૌદ્ધ ધર્મમાં નિર્વાણની કલ્પના સમજાવો.",
                "બૌદ્ધ પ્રથા માં ધ્યાનનું મહત્વ શું છે?",
                "મહાયાન અને થેરવાદ બૌદ્ધ ધર્મમાં શું તફાવત છે તે સમજાવો."
            ],
            "Chinese (Simplified)": [
                "谁是悉达多·乔达摩，他在佛教中为什么重要？",
                "什么是四圣谛？",
                "简要解释佛教中的涅槃概念。",
                "冥想在佛教修行中有什么重要性？",
                "描述大乘佛教和上座部佛教的区别。"
            ],
            "Thai": [
                "ใครคือสิทธัตถะ โคตมะ และทำไมเขาจึงสำคัญในพุทธศาสนา?",
                "อริยสัจ 4 คืออะไร?",
                "อธิบายแนวคิดเรื่องนิพพานในพุทธศาสนา",
                "การทำสมาธิมีความสำคัญอย่างไรในพุทธศาสนา?",
                "อธิบายความแตกต่างระหว่างพุทธศาสนามหายานและเถรวาท"
            ]
        }

        # Default questions
        self.default_questions = self.test_questions["English"]

        self.retriever = RAGRetriever()
        self.results = []

    def get_test_questions(self, language):
        """Get test questions for a specific language"""
        return self.test_questions.get(language, self.default_questions)

    def test_translation_only(self, text, src_lang, tgt_lang):
        """Test just the translation function"""
        try:
            start_time = time.time()
            translated = translate(text, src_lang, tgt_lang)
            end_time = time.time()

            success = translated != text and not translated.startswith("[Translation error")

            return {
                "success": success,
                "original": text[:50] + "..." if len(text) > 50 else text,
                "translated": translated[:50] + "..." if len(translated) > 50 else translated,
                "time_taken": round(end_time - start_time, 2),
                "error": None if success else "Translation failed or returned original text"
            }
        except Exception as e:
            return {
                "success": False,
                "original": text[:50] + "..." if len(text) > 50 else text,
                "translated": f"ERROR: {str(e)}",
                "time_taken": 0,
                "error": str(e)
            }

    def test_full_pipeline(self, question, input_lang, output_lang):
        """Test the full pipeline: input translation + RAG + output translation"""
        try:
            print(f"Testing: {input_lang} → English → {output_lang}")

            # Step 1: Translate input to English (if needed)
            if input_lang != "English":
                english_question = translate(question, input_lang, "English")
            else:
                english_question = question

            # Step 2: Get RAG response
            result = self.retriever.get_response(english_question)
            english_answer = result.get("answer", "").strip()

            if not english_answer:
                return {
                    "success": False,
                    "error": "RAG returned empty response",
                    "input_translation": english_question,
                    "rag_response": "",
                    "final_output": "",
                    "time_taken": 0
                }

            # Step 3: Translate output (if needed)
            start_time = time.time()

            if output_lang != "English":
                translated_answer = translate(english_answer, "English", output_lang)
                final_response = f"(Responding in {output_lang}) {translated_answer}"
                translation_success = translated_answer != english_answer
            else:
                final_response = english_answer
                translation_success = True

            end_time = time.time()

            return {
                "success": translation_success and bool(english_answer),
                "error": None,
                "input_translation": english_question[:100] + "..." if len(english_question) > 100 else english_question,
                "rag_response": english_answer[:100] + "..." if len(english_answer) > 100 else english_answer,
                "final_output": final_response[:100] + "..." if len(final_response) > 100 else final_response,
                "time_taken": round(end_time - start_time, 2)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "input_translation": "",
                "rag_response": "",
                "final_output": "",
                "time_taken": 0
            }

    def run_translation_tests(self):
        """Test all language pair combinations for translation only"""
        print("=== TRANSLATION ONLY TESTS ===")

        total_tests = 0
        successful_tests = 0

        for src_lang in self.languages:
            for tgt_lang in self.languages:
                if src_lang == tgt_lang:
                    continue

                questions = self.get_test_questions(src_lang)

                for i, question in enumerate(questions[:2]):  # Test 2 questions per combo
                    total_tests += 1
                    print(f"Testing {total_tests}: {src_lang} → {tgt_lang}")

                    result = self.test_translation_only(question, src_lang, tgt_lang)

                    if result["success"]:
                        successful_tests += 1
                        print(f"  ✅ SUCCESS ({result['time_taken']}s)")
                    else:
                        print(f"  ❌ FAILED: {result['error']}")

                    self.results.append({
                        "test_type": "translation_only",
                        "src_lang": src_lang,
                        "tgt_lang": tgt_lang,
                        "question_num": i + 1,
                        "success": result["success"],
                        "time_taken": result["time_taken"],
                        "error": result["error"],
                        "original": result["original"],
                        "translated": result["translated"]
                    })

                    time.sleep(0.5)

        print(f"\n=== TRANSLATION SUMMARY ===")
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests / total_tests) * 100:.1f}%")

    def run_full_pipeline_tests(self, sample_combos=10):
        """Test the full pipeline for a sample of language combinations"""
        print(f"\n=== FULL PIPELINE TESTS (Sample of {sample_combos}) ===")

        all_combos = list(itertools.product(self.languages, self.languages))
        all_combos = [(src, tgt) for src, tgt in all_combos if src != tgt]

        import random
        test_combos = random.sample(all_combos, min(sample_combos, len(all_combos)))

        total_tests = 0
        successful_tests = 0

        for src_lang, tgt_lang in test_combos:
            questions = self.get_test_questions(src_lang)
            question = questions[0]

            total_tests += 1
            print(f"\nTesting {total_tests}: {src_lang} → {tgt_lang}")
            print(f"Question: {question[:50]}...")

            result = self.test_full_pipeline(question, src_lang, tgt_lang)

            if result["success"]:
                successful_tests += 1
                print(f"  ✅ SUCCESS ({result['time_taken']}s)")
            else:
                print(f"  ❌ FAILED: {result['error']}")

            self.results.append({
                "test_type": "full_pipeline",
                "src_lang": src_lang,
                "tgt_lang": tgt_lang,
                "question_num": 1,
                "success": result["success"],
                "time_taken": result["time_taken"],
                "error": result["error"],
                "input_translation": result["input_translation"],
                "rag_response": result["rag_response"],
                "final_output": result["final_output"]
            })

            time.sleep(1)

        print(f"\n=== FULL PIPELINE SUMMARY ===")
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests / total_tests) * 100:.1f}%")

    def save_results(self, filename=None):
        """Save test results to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translation_test_results_{timestamp}.csv"

        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"\n📊 Results saved to: {filename}")

        total = len(df)
        successful = len(df[df['success'] == True])
        print(f"\n=== OVERALL SUMMARY ===")
        print(f"Total tests run: {total}")
        print(f"Successful tests: {successful}")
        print(f"Failed tests: {total - successful}")
        print(f"Overall success rate: {(successful / total) * 100:.1f}%")

        print(f"\n=== BY TEST TYPE ===")
        for test_type in df['test_type'].unique():
            subset = df[df['test_type'] == test_type]
            success_rate = (len(subset[subset['success'] == True]) / len(subset)) * 100
            print(f"{test_type}: {success_rate:.1f}% success rate")

    def run_all_tests(self, sample_pipeline_tests=10):
        """Run all tests"""
        print("Starting automated translation testing...")
        print(f"Languages to test: {', '.join(self.languages)}")

        self.run_translation_tests()
        self.run_full_pipeline_tests(sample_pipeline_tests)
        self.save_results()


if __name__ == "__main__":
    tester = TranslationTester()

    # Run quick test
    print("Running QUICK test...")
    tester.run_all_tests(sample_pipeline_tests=5)

    # For full tests:
    # tester.run_all_tests(sample_pipeline_tests=20)
