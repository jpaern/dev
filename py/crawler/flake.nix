{
  description = "Simple python web crawler";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [ ]);
      in {
        devShell = pkgs.mkShell {
          name = "python web crawler dev shell";
          buildInputs = [
            pythonEnv
            pkgs.gcc # C compiler
            pkgs.cmake # Build system generator
            pkgs.pkg-config
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
          shellHook = ''
            # fixes libstdc++ issues and libz.so issues
            LD_LIBRARY_PATH="${
              pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc pkgs.zlib ]
            }":$LD_LIBRARY_PATH;
          '';
        };
      });
}
