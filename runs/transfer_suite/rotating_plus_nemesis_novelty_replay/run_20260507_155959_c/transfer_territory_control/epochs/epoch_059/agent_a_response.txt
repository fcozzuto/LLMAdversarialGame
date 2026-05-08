def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c is not None and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c is not None and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c is not None and len(c) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in opp_t:
            cat = 2
            steal_bonus = 9
        elif (nx, ny) in unclaimed:
            cat = 1
            steal_bonus = 5
        elif (nx, ny) in self_t:
            cat = 0
            steal_bonus = 0
        else:
            cat = 0
            steal_bonus = -1

        # Prefer interior while aggressively grabbing/stealing nearby edge-claims.
        val = 10 * cat + steal_bonus - 0.5 * d_center + 0.15 * (d_opp == 0) - 0.05 * d_opp
        if best is None or (val > best_val) or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]