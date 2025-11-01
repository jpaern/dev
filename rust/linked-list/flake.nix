{
  description = "A devShell example";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    #rust-overlay.url = "github:oxalica/rust-overlay";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      # rust-overlay,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        # overlays = [ (import rust-overlay) ];
        # pkgs = import nixpkgs { inherit system overlays; };
        pkgs = import nixpkgs { inherit system; };
      in
      with pkgs;
      {
        devShells.default = mkShell {
          buildInputs = [
            openssl
            pkg-config
            eza
            fd
            cargo
            rust-analyzer
            rustc
            rustfmt
          ];

          CARGO_INSTALL_ROOT = "${toString ./.}/.cargo";
          RUST_SRC_PATH = rustPlatform.rustLibSrc;
          shellHook = ''
            alias ls=eza
            alias find=fd
          '';
        };
      }
    );
}
