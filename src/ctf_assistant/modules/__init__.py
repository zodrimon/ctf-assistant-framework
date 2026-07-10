"""
Investigation modules package.
"""

from ctf_assistant.modules.forensics.file_analysis.module import FileAnalysisModule
from ctf_assistant.modules.forensics.archives.module import ArchivesModule
from ctf_assistant.modules.forensics.pcap.module import PcapModule
from ctf_assistant.modules.forensics.memory.module import MemoryModule
from ctf_assistant.modules.forensics.steganography.module import SteganographyModule
from ctf_assistant.modules.forensics.disk.module import DiskModule
from ctf_assistant.modules.forensics.log_analysis.module import LogAnalysisModule
from ctf_assistant.modules.forensics.malware_triage.module import MalwareTriageModule

MODULES = {
    "File Analysis": FileAnalysisModule,
    "Archives": ArchivesModule,
    "PCAP Analysis": PcapModule,
    "Memory (Volatility)": MemoryModule,
    "Steganography": SteganographyModule,
    "Disk Image": DiskModule,
    "Log Analysis": LogAnalysisModule,
    "Malware Triage (YARA)": MalwareTriageModule,
}
