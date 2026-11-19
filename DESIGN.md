# AiCoN profile cards

Original SVG implementation for the AiCoN GitHub profile. Visual approach inspired by https://www.avivashishta.com/blog/github-profile-readme-animated-svg-cards . No source code or artwork was copied from that article or its repository.

Cards use AiCoN orange, cream and sage, with separate dark/light and narrow-screen versions. Fonts are self-contained Outfit subsets, distributed with their SIL Open Font License in cards/fonts/OFL.txt. The logo is the existing AiCoN mark.

Run `python update_profile.py` to fetch public data and redraw. Run `STATIC=1 python scripts/render_cards.py` for final-frame SVGs. Run without STATIC to restore animation before committing. Reduced-motion mode disables CSS animation and the moving calendar trail. Nothing runs inside the README except native SVG animation.

The archive parser counts unique article links, not visits. Website commit activity and the public GitHub calendar are separate sources with different counting rules. Refresh errors preserve prior generated files; the visible timestamp is the last successful refresh.
