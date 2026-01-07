
from gtts import gTTS
import os

long_text = """Hey there, and welcome to our channel. As you know, living in today's fast-paced world can be overwhelming, especially when we're dealing with multiple responsibilities and tasks. But here's the thing - we've got the power to break free from stress and anxiety. In today's video, we're going to look at three simple yet effective strategies to help you manage stress, so let's dive right in.

Firstly, let's talk about prioritization. One of the main reasons we feel overwhelmed is because we're taking on too much at once. By prioritizing our tasks, we focus on what's really important and delegate, defer, or delete the rest. Think of it like this - imagine you're trying to eat a huge pizza all by yourself. You wouldn't eat the whole pizza in one sitting because it's too much to handle, right? Same thing with tasks - break them down into smaller, manageable chunks.

Another thing that can make us feel stressed is our inability to say no. By setting healthy boundaries, we can protect our time and energy. Remember, it's okay to say no, especially when it's for your own good. You don't need to justify your decision to anyone, either - just a simple 'no, thank you' is enough.

Lastly, let's talk about mindful self-care. When we're stressed, our minds go into overdrive, and we start worrying about everything. But here's the thing - our thoughts don't define our reality. We can choose to think more positively, which in turn, impacts our mood, behavior, and overall well-being. Try taking a few minutes each day to practice deep breathing exercises, meditation, or yoga. It may seem weird, but trust me, it works wonders.

So, there you have it - three simple strategies to help you break the cycle of overwhelm. Remember, stress less, not more. You got this, and you deserve to live a stress-free life.

Relax, breathe, and remember - you're in control."""

try:
    print("Generating TTS for long text...")
    tts = gTTS(text=long_text, lang='en', slow=False)
    tts.save("test_tts.mp3")
    print("TTS generation complete. Check test_tts.mp3 duration/size.")
    
    # Check size
    size = os.path.getsize("test_tts.mp3")
    print(f"File size: {size} bytes")
    
except Exception as e:
    print(f"Error: {e}")
