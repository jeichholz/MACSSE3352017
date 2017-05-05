(TeX-add-style-hook
 "Hw7"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("geometry" "margin=1in")))
   (TeX-run-style-hooks
    "latex2e"
    "MA335defs"
    "article"
    "art10"
    "geometry"
    "mathtools")))

