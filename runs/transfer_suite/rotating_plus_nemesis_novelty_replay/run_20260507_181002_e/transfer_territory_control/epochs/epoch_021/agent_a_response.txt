def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if not unclaimed:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Deterministic ordering for tie-breaks
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**9), 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_opp = (nx, ny) in oppT
        is_uncl = (nx, ny) in unclaimed
        is_self = (nx, ny) in selfT

        # Favor capturing opponent; then expanding into unclaimed; keep near center;
        # slightly prefer moving away from opponent to avoid mirror collisions.
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        d_opp = abs(nx - ox) + abs(ny - oy)

        score = 0
        score += 100.0 if is_opp else 0.0
        score += 12.0 if is_uncl else 0.0
        score += 2.0 if is_self else 0.0
        score += 0.5 * center
        score += 0.05 * d_opp

        # Tie-break deterministically by move index and turn parity
        k = moves.index((dx, dy))
        score2 = score + (0.0001 * ((observation.get("turn_index", 0) + k) % 2))
        if score2 > best[0]:
            best = (score2, dx, dy)

    # Fallback: stay if all moves filtered out (should be rare)
    return [int(best[1]), int(best[2])]