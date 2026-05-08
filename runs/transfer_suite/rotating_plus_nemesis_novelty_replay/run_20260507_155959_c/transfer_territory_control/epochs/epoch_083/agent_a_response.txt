def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for c in (observation.get("self_territory") or []):
        if c is not None and len(c) >= 2:
            self_t.add((int(c[0]), int(c[1])))
    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c is not None and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))
    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c is not None and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def adj_to_own(x, y):
        return any((x + dx, y + dy) in self_t for dx, dy in neigh)

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in opp_t:
            score += 5
        elif (nx, ny) in unclaimed:
            score += 3
        if (nx, ny) not in self_t:
            score += 1 if adj_to_own(nx, ny) else 0
        # Prefer pushing toward opponent and away from self-edges
        score += -0.05 * (abs(nx - ox) + abs(ny - oy))
        # Soft bias to avoid going deep into our own already-controlled cells
        score += -0.1 * (1 if (nx, ny) in self_t else 0)
        tie = (score, -abs(nx - ox) - abs(ny - oy), -abs(nx - sx) - abs(ny - sy), dx, dy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
        elif best is not None and score == best_score:
            if tie > (best_score, -abs(best[0] + sx - ox) - abs(best[1] + sy - oy), -abs(best[0]) - abs(best[1]), best[0], best[1]):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]