
from app.integrations.llm.writing.explanation import generate_writing_evaluation


prompt="আমি প্রতিদিন সকালে পার্কে হাঁটতে যাই। আমি সেখানে আমার বন্ধুদের সাথে দেখা করি এবং আমরা কিছুক্ষণ কথা বলি। এরপর আমি বাসায় ফিরে নাস্তা করি।"
answer="I go to park every morning. I meet with my friends there and we talks for sometimes. After that, I return to home and take breakfast."

data = generate_writing_evaluation(
    answer = answer,
    prompt_text= prompt
)
print(data)