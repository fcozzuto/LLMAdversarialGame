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
    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    def adj_count(x, y, s):
        cnt = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in s:
                cnt += 1
        return cnt

    moves = []
    best = None
    # Deterministic tie-break order: (dx,dy) in fixed sequence
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0) or True:
                moves.append((dx, dy))
    ordered = sorted(set(moves), key=lambda t: (t[0], t[1]))

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps in place on invalid
        score = 0
        if (nx, ny) in opp_t:
            score += 6 + 2 * adj_count(nx, ny, opp_t)
        elif (nx, ny) in unclaimed:
            score += 4 + 3 * adj_count(nx, ny, opp_t)
        elif (nx, ny) in self_t:
            score += 1
        else:
            score += 0

        score += 0.4 * adj_count(nx, ny, unclaimed)
        score -= 0.6 * abs(nx - ox) - 0.05 * abs(ny - oy)  # mild pursuit of opponent-side
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]