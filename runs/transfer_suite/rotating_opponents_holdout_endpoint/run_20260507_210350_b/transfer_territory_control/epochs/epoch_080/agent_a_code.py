def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    # Target frontier near opponent territory (edge-claim defense/attack)
    opp_edges = set()
    for x, y in opp_terr:
        for nx, ny in neigh8(x, y):
            if (nx, ny) in unclaimed:
                opp_edges.add((nx, ny))
    if not opp_edges:
        opp_edges = set(unclaimed)
    if not opp_edges:
        # Fallback: move toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        # Deterministic pick: closest to self; tie-break by coordinates
        tx, ty = min(opp_edges, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))

    def immediate_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        val = 0.0
        if (x, y) in opp_terr:
            val += 8.0  # flipping on entry
        if (x, y) in self_terr:
            val += 1.0
        if (x, y) in unclaimed:
            val += 4.0
        # Encourage approaching target frontier; discourage moving away
        val += -0.25 * (abs(tx - x) + abs(ty - y))
        # Obstacle proximity penalty
        prox = 0
        for nx, ny in neigh8(x, y):
            if (nx, ny) in obstacles:
                prox += 1
        val += -1.2 * prox
        return val

    best_dx, best_dy = 0, 0
    best_val = -10**18
    # Secondary goal: avoid letting opponent get closer to its own frontier
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = immediate_value(nx, ny)
        # Slightly discourage staying put if a better move exists
        if dx == 0 and dy == 0:
            v -= 0.05
        # Nudge: if we can reduce distance to opponent position, do it modestly
        v += 0.04 * (-(abs(nx - ox) + abs(ny - oy)))
        if v > best_val or (v == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = v
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]