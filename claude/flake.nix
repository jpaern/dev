{
  description = "Dev shell with Claude Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          # claude-code ist unfree -> muss explizit erlaubt werden
          config.allowUnfree = true;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.claude-code
            # Weitere Tools hier ergänzen, z.B.:
            # pkgs.nodejs_22
            # pkgs.git
          ];

          shellHook = ''
            echo "Claude Code ready -> 'claude' zum Starten"
          '';
        };
      }
    );
}
