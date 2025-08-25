#!/usr/bin/env python3
"""
Audio debugging script to diagnose TTS and audio system issues.
"""

import pyttsx3
import time
import os
import subprocess
import sys

def check_windows_audio():
    """Check Windows audio system"""
    print("🔧 Checking Windows Audio System...")
    
    try:
        # Check if audio service is running
        result = subprocess.run(['sc', 'query', 'AudioSrv'], 
                              capture_output=True, text=True, shell=True)
        if 'RUNNING' in result.stdout:
            print("✅ Windows Audio Service is running")
        else:
            print("❌ Windows Audio Service may not be running")
            
        # Check audio devices
        result = subprocess.run(['powershell', '-Command', 
                               'Get-AudioDevice -List | Format-Table -AutoSize'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("📋 Audio Devices:")
            print(result.stdout)
        
    except Exception as e:
        print(f"⚠️  Could not check Windows audio: {e}")

def test_tts_basic():
    """Basic TTS testing"""
    print("\n🎤 Basic TTS Testing...")
    
    try:
        # Initialize engine
        engine = pyttsx3.init()
        print(f"✅ TTS Engine initialized")
        
        # Get engine info
        voices = engine.getProperty('voices')
        print(f"📋 Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, v in enumerate(voices[:3]):  # Show first 3 voices
                print(f"   {i+1}. {v.name}")
        
        # Test properties
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')
        
        print(f"📊 Current settings:")
        print(f"   Rate: {rate}")
        print(f"   Volume: {volume}")
        
        # Set good properties
        engine.setProperty('volume', 1.0)
        engine.setProperty('rate', 120)  # Slower for clarity
        
        print("🔊 Testing speech output...")
        
        # Test with simple phrase
        test_phrase = "Hello, this is a test of the text to speech system."
        print(f"🎤 Test phrase: '{test_phrase}'")
        
        try:
            engine.say(test_phrase)
            engine.runAndWait()
            print("   ✅ Direct speech completed")
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ Direct speech failed: {e}")
        
        # Test file method
        try:
            print("   Testing file method...")
            temp_file = "test_audio.wav"
            engine.save_to_file(test_phrase, temp_file)
            engine.runAndWait()
            
            if os.path.exists(temp_file):
                print(f"   ✅ Audio file created: {temp_file}")
                # Try to play with Windows media player
                subprocess.run(['start', '', temp_file], shell=True)
                time.sleep(2)
                os.remove(temp_file)
            else:
                print("   ❌ Audio file not created")
                
        except Exception as e:
            print(f"   ❌ File method failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def check_audio_troubleshooting():
    """Provide audio troubleshooting tips"""
    print("\n🔧 Audio Troubleshooting Tips:")
    print("=" * 50)
    print("1. Check Windows Volume Mixer (right-click speaker icon)")
    print("2. Ensure Python.exe is not muted in Volume Mixer")
    print("3. Check default audio output device")
    print("4. Try different audio output (speakers vs headphones)")
    print("5. Check Windows Sound settings (Settings > System > Sound)")
    print("6. Try running as Administrator")
    print("7. Check audio drivers are up to date")
    print("8. Restart Windows Audio service if needed")

if __name__ == "__main__":
    print("🎵 AUDIO DEBUG UTILITY")
    print("=" * 50)
    
    check_windows_audio()
    test_tts_basic()
    check_audio_troubleshooting()
    
    print("\n" + "=" * 50)
    print("🎯 DEBUG COMPLETE")
    print("\nIf you still can't hear audio:")
    print("1. Check Volume Mixer for Python")
    print("2. Try running as Administrator")
    print("3. Check default audio device")
    print("4. Test with headphones vs speakers")
