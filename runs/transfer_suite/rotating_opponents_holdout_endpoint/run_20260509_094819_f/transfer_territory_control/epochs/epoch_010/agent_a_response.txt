def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    cx_i, cy_i = int(cx + 0.5), int(cy + 0.5)

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    self_count = int(observation.get("self_territory_count", 0) or 0)
    aggressive = 1 if self_count >= opp_count else 2

    best_move = (0, 0, sx, sy)
    best_score = -10**18
    best_tie = (0, 0)

    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in resources:
            score += 80
        if (nx, ny) in unclaimed:
            score += 55
        if (nx, ny) in opp_terr:
            score += 35 * aggressive
        if (nx, ny) in self_terr:
            score -= 6

        # Prefer moving toward frontier: lots of unclaimed/opp-territory in neighborhood
        neigh = 0
        neigh_un = 0
        neigh_opp = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if not inb(ax, ay) or (ax, ay) in obstacles:
                    continue
                if (ax, ay) in unclaimed:
                    neigh_un += 1
                if (ax, ay) in opp_terr:
                    neigh_opp += 1
                if (ax, ay) in unclaimed or (ax, ay) in opp_terr:
                    neigh += 1
        score += 7 * neigh_un + 5 * neigh_opp

        # Mild center attraction to avoid stalling near edges
        score += -0.5 * man(nx, ny, cx_i, cy_i)

        # Avoid getting stuck: small penalty for continuing on same cell
        if dx == 0 and dy == 0:
            score -= 3

        # Deterministic tie-breaker: minimal manhattan to best local target, then lexicographic
        tie = (man(nx, ny, cx_i, cy_i), abs(dx) + abs(dy), dx, dy)
        if score > best_score or (score == best_score and tie < best_tie):
            best_score = score
            best_move = (dx, dy, nx, ny)
            best_tie = tie

    return [best_move[0], best_move[1]]