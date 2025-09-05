{
  description = "Test for Haskell opt parser";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
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
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.haskell.compiler.ghc984 # Aktuelle GHC-Version anpassen!
            pkgs.cabal-install
            pkgs.haskellPackages.hlint
            pkgs.haskellPackages.haskell-language-server
            pkgs.pkg-config
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];
          shellHook = ''
            # fixes libstdc++ issues and libz.so issues
            LD_LIBRARY_PATH="${
              pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc
                pkgs.zlib
              ]
            }":$LD_LIBRARY_PATH;
            echo "Wellcome in a Haskell-Dev environment!"
          '';
        };
      }
    );
}
