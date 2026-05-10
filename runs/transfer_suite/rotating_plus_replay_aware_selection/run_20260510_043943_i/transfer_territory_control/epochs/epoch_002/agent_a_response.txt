def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    self_territory = observation.get("self_territory", [])
    opp_territory = observation.get("opponent_territory", [])
    self_set = set((p[0], p[1]) for p in self_territory if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((p[0], p[1]) for p in opp_territory if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells", [])
    uc = [(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]
    resources = observation.get("resources", [])
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def min_dist_to_list(x, y, lst):
        if not lst:
            return 10**9
        md = 10**9
        for px, py in lst:
            d = man(x, y, px, py)
            if d < md:
                md = d
        return md

    best = None
    bestv = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Strongly prefer cells we can flip immediately.
        flip_bonus = 0
        if (nx, ny) in opp_set:
            flip_bonus = 1000

        # Center pressure: opponent archetype claims near center, so mirror while expanding your control.
        dist_center = abs(nx - cx) + abs(ny - cy)

        # Expansion: move toward nearest unclaimed/resource; if none visible, approach opponent territory edge.
        d_uc = min_dist_to_list(nx, ny, uc)
        d_res = min_dist_to_list(nx, ny, res)
        d_opp_edge = min_dist_to_list(nx, ny, list(opp_set)) if opp_set else man(nx, ny, ox, oy)

        # Prefer staying connected to our territory (avoid isolated jumps).
        d_self = min_dist_to_list(nx, ny, list(self_set)) if self_set else 0

        v = 0
        v += flip_bonus
        v += -2.0 * dist_center
        v += -0.9 * d_uc
        v += -0.5 * d_res
        v += -0.2 * d_opp_edge  # slightly reduce distance to their claim boundary
        v += -0.05 * d_self   # keep coherence

        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]