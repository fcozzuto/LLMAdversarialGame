def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" not in self_role and "purs" in opp_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = deltas[:]  # deterministic

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Candidate evaluation
    best = None
    best_score = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d2 = dist2(nx, ny, ox, oy)
        # Obstacle proximity penalty (discourage hugging walls/obstacles)
        prox = 0
        for (bx, by) in blocked:
            dd = abs(nx - bx) + abs(ny - by)
            if dd == 0:
                prox += 10
            elif dd <= 2:
                prox += 4 - dd
        # If evading (rare), maximize distance; otherwise minimize
        base = d2 if not pursuer else -d2
        # Small preference to reduce/maintain approach in both axes to catch zigzags
        ax_sgn = 0
        if nx != ox: ax_sgn = 0 if nx == ox else (-abs(nx - ox) if pursuer else abs(nx - ox))
        ay_sgn = 0
        if ny != oy: ay_sgn = 0 if ny == oy else (-abs(ny - oy) if pursuer else abs(ny - oy))
        approach = (ax_sgn + ay_sgn)
        # Tie-breaker: deterministic lexicographic by delta order
        score = base + 0.15 * approach - 0.35 * prox
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best