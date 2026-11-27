from memory import EpisodicMemory

memory = EpisodicMemory()

memory.add_memory(
    event="Professor discussed an assignment",
    location="Classroom",
    activity="Lecture",
    cognitive_state="Engaged"
)

print("\nMEMORIES:")

for item in memory.get_memories():
    print(item)

print("\nSEARCH:")

for item in memory.search("assignment"):
    print(item)