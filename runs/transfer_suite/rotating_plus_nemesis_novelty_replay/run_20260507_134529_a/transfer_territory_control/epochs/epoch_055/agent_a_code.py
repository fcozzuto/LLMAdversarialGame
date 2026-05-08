def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-breaking order favors diagonals slightly (more exploration)
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]) == 0, -(t[0] != 0 and t[1] != 0), t[0], t[1]))

    # Precompute a small set of nearby unclaimed cells to avoid full-grid search
    nearby_unclaimed = []
    for (ux, uy) in unclaimed:
        d = abs(ux - sx) + abs(uy - sy)
        if d <= 4:
            nearby_unclaimed.append((ux, uy))
    if not nearby_unclaimed and unclaimed:
        # fallback: closest few deterministically
        arr = list(unclaimed)
        arr.sort(key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        nearby_unclaimed = arr[:6]

    def score_cell(x, y):
        # cell type
        if (x, y) in obstacles:
            return -10**12
        if (x, y) in self_terr:
            base = 1.5
        elif (x, y) in opp_terr:
            # flipping is allowed; reward only if it also reduces distance to our controlled area
            base = 2.2
        elif (x, y) in unclaimed:
            base = 4.5
        else:
            base = 0.6

        # risk: stay away from opponent to avoid being swept
        d_opp = max(0, abs(x - ox) + abs(y - oy))
        risk = -3.5 / (1 + d_opp)

        # attraction to nearby unclaimed
        if nearby_unclaimed:
            dmin = 10**9
            for (ux, uy) in nearby_unclaimed:
                d = abs(ux - x) + abs(uy - y)
                if d < dmin:
                    dmin = d
            attract = 3.0 / (1 + dmin)
        else:
            attract = 0.0

        # slight preference for moves that increase distance from opponent if entering opponent territory is risky
        opp_terr_bonus = 0.0
        if (x, y) in opp_terr:
            opp_terr_bonus = 1.0 * (d_opp > 2)
        return base + attract + risk + opp_terr_bonus

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = score_cell(nx, ny)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]