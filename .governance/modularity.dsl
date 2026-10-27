modularity edialog version 0.4.4

module core {
  owns: ["src/edialog/models.py", "src/edialog/errors.py", "src/edialog/affect.py", "src/edialog/vision.py"]
}

module engines {
  owns: ["src/edialog/engine.py", "src/edialog/fiction.py", "src/edialog/nl.py", "src/edialog/backends.py"]
  depends_on: [core]
}

module process_mcp {
  owns: ["src/edialog/pipeline.py", "src/edialog/mcp.py", "dockuri.json", "dockuri.yaml", "uriprocess.json"]
  depends_on: [core, engines]
}
