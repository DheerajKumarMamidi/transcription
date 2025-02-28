import os
import argparse
import shutil

def delete_files(directory, dry_run=False):
    """Delete all generated transcription files (_audio.wav, _converted.wav, _transcription.txt)."""
    deleted_files = []
    
    for file in os.listdir(directory):
        if file.endswith(("_audio.wav", "_converted.wav", "_transcription.txt", "_fixed.wav")):
            file_path = os.path.join(directory, file)
            deleted_files.append(file_path)

            if not dry_run:
                os.remove(file_path)

    folder = "transcriptions"
    
    if not os.path.exists(folder):
        return

    try:
        shutil.rmtree(folder)  # Delete the entire folder
        deleted_files.append("Transcriptions Folder deleted")
    except Exception as e:
        print(f"❌ Error deleting '{folder}': {e}")

    return deleted_files



# === Handle Command-Line Arguments ===
parser = argparse.ArgumentParser(description="Delete all generated transcription files.")
parser.add_argument("directory", nargs="?", default=".", help="Directory to clean (default: current directory)")
parser.add_argument("--dry-run", action="store_true", help="Show files that will be deleted without deleting them")
args = parser.parse_args()

# === Run Cleanup ===
deleted_files = delete_files(args.directory, dry_run=args.dry_run)

if deleted_files:
    print("\n🗑️ The following were deleted:" if not args.dry_run else "\n🔍 Files that would be deleted:")
    for file in deleted_files:
        print(f"   - {file}")
else:
    print("\n✅ Nothing found to delete.")

if args.dry_run:
    print("\n💡 Run the script without `--dry-run` to actually delete the files.")
