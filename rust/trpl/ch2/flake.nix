{
  description = "Rust-Entwicklungsumgebung";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      rust-overlay,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f (
            import nixpkgs {
              inherit system;
              overlays = [ rust-overlay.overlays.default ];
            }
          )
        );
    in
    {
      devShells = forAllSystems (
        pkgs:
        let
          inherit (pkgs) lib stdenv;

          # Liegt im Projekt eine rust-toolchain.toml (git-tracked), wird sie verwendet,
          # sonst das aktuelle stabile Rust mit den wichtigsten Komponenten.
          rustToolchain =
            if builtins.pathExists ./rust-toolchain.toml then
              pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml
            else
              pkgs.rust-bin.stable.latest.default.override {
                extensions = [
                  "rust-src"
                  "rust-analyzer"
                  "clippy"
                  "rustfmt"
                ];
              };
        in
        {
          default = pkgs.mkShell {
            packages = [
              # Toolchain: rustc, cargo, clippy, rustfmt, rust-analyzer, rust-src
              rustToolchain

              # Cargo-Erweiterungen
              pkgs.cargo-nextest # schnellerer Test-Runner
              pkgs.cargo-edit # cargo upgrade / cargo set-version
              pkgs.cargo-outdated # veraltete Abhängigkeiten anzeigen
              pkgs.cargo-audit # Sicherheitslücken in Abhängigkeiten
              pkgs.cargo-deny # Lizenz- und Abhängigkeits-Policies
              pkgs.cargo-expand # Makros expandieren
              pkgs.cargo-machete # ungenutzte Abhängigkeiten finden
              pkgs.bacon # Hintergrund-Checker (Nachfolger von cargo-watch)

              # Native Abhängigkeiten, die viele Crates brauchen (openssl-sys u. a.)
              pkgs.pkg-config
              pkgs.openssl

              # Debugging
              pkgs.lldb
            ]
            ++ lib.optionals stdenv.isLinux [
              pkgs.gdb
              pkgs.mold # schneller Linker (optional per .cargo/config.toml aktivieren)
            ]
            ++ lib.optionals stdenv.isDarwin [
              pkgs.libiconv
            ];

            # Für rust-analyzer und Editoren, die die Std-Quellen suchen
            RUST_SRC_PATH = "${rustToolchain}/lib/rustlib/src/rust/library";
            RUST_BACKTRACE = "1";

            shellHook = ''
              echo "Rust-Umgebung: $(rustc --version)"
            '';
          };
        }
      );
    };
}
