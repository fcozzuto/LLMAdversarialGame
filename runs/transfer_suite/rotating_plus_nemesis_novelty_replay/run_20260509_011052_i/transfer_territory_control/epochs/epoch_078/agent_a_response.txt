def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def to_set(key):
        s = set()
        for p in (observation.get(key, []) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")
    resources = to_set("resources")

    targets = resources if resources else unclaimed
    if not targets:
        targets = unclaimed if unclaimed else (opp_terr if opp_terr else {(ox, oy)})

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Precompute frontier distances (small lists, 8x8)
    opp_list = list(opp_terr)
    def min_dist_to_set(x, y, S_list):
        md = 10**9
        for (a, b) in S_list:
            d = abs(a - x) + abs(b - y)
            if d < md: md = d
        return md if S_list else md

    best = (None, -10**18)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        land = (nx, ny)

        # Immediate capture value
        if land in opp_terr:
            cap = 120
        elif land in targets:
            cap = 35
        elif land in self_terr:
            cap = 8
        else:
            cap = 4

        # Strategic shaping: counter "territory_counterclaim" by avoiding getting trapped
        d_to_target = min_dist_to_set(nx, ny, list(targets))
        d_to_opp = min_dist_to_set(nx, ny, opp_list)
        # Prefer staying away unless we are actually landing on opponent territory
        avoid = (0 if land in opp_terr else (10 / (1 + d_to_opp)))
        # Also prefer closing distance to targets
        close = (0 if d_to_target >= 10**8 else (18 / (1 + d_to_target)))

        # Minor tie-breaker to keep progress toward opponent side deterministically
        towards_opp = (0 if cap < 30 else (abs(ox - nx) + abs(oy - ny)) * -0.01)

        val = cap + close - avoid + towards_opp
        if val > best[1] or (val == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), val)

    if best[0] is None:
        return [0, 0]
    dx, dy = best[0]
    return [int(dx), int(dy)]