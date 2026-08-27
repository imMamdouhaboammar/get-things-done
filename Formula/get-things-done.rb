class GetThingsDone < Formula
  desc "Execution skill pack with portable adapters for AI coding agents"
  homepage "https://github.com/imMamdouhaboammar/get-things-done"
  head "https://github.com/imMamdouhaboammar/get-things-done.git", branch: "main"

  depends_on "python@3.13"

  def install
    libexec.install "skills", "scripts", "adapters", "plugin.json", "skills.sh.json", "kimi.plugin.json"
    libexec.install ".claude-plugin", ".codex-plugin"
    bin.write_exec_script libexec/"scripts/gtd.py"
  end

  def caveats
    <<~EOS
      GTD's canonical Agent Skills are installed under:
        #{opt_libexec}/skills

      To copy them into a host-specific user skill root, use the repository
      shell installer or copy the two skill directories from that location.

      This formula is HEAD-only until GTD publishes a stable Homebrew release artifact.
    EOS
  end

  test do
    system bin/"gtd", "doctor"
  end
end
