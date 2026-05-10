def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        dopp = abs(x - ox) + abs(y - oy)
        # Prefer expanding into unclaimed; then into our own territory; allow flipping opponent if closer,
        # but avoid walking directly into their likely sweep front by repulsion from opponent/opp territory.
        if (x, y) in unclaimed:
            base = 6.0
        elif (x, y) in self_terr:
            base = 3.0
        elif (x, y) in opp_terr:
            base = 2.0
        else:
            base = 1.0
        opp_repulse = 4.0 / (dopp + 1.0)
        opp_terr_pen = (1.5 if (x, y) in opp_terr else 0.0)
        return base + opp_repulse - opp_terr_pen

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    moves.append((0, 0))

    # Deterministic tie-break: (value desc, farther from opponent if unclaimed equally good, then lexicographic)
    best = (float("-inf"), 0.0, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = cell_value(nx, ny)
        dopp = abs(nx - ox) + abs(ny - oy)
        far = float(dopp)
        cand = (v, far, dx, dy)
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] > best[1]) or (cand[0] == best[0] and cand[1] == best[1] and (dx, dy) < (best[2], best[3])):
            best = cand

    return [int(best[2]), int(best[3])]