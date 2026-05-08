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
    unclaimed |= toset(observation.get("resources"))

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp_edge(x, y):
        return (x == 0) + (x == w - 1) + (y == 0) + (y == h - 1)

    def score_cell(x, y):
        d = abs(x - ox) + abs(y - oy)
        if (x, y) in obstacles:
            return -10**9
        is_un = (x, y) in unclaimed
        is_opp = (x, y) in oppT
        is_self = (x, y) in selfT
        # Territory expansion: prioritize unclaimed far from opponent; capture opp only if it also increases separation.
        base = 0
        base += 260 if is_un else 0
        base += 140 if is_opp else 0
        base += 10 if is_self else 0
        # Safety: avoid moving into positions close to opponent unless capturing.
        base += 35 * d
        if d <= 1:
            base -= 120 if not is_opp else 40
        # Frontier: slightly prefer edges to reduce opponent's sweep access.
        base += 20 * clamp_edge(x, y)
        # Encourage moving outwards (away from your current territory clusters).
        base += 6 * (1 if (x, y) not in selfT else 0)
        return base

    best = (score_cell(sx, sy), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)
    dx, dy = best[1], best[2]
    return [int(dx), int(dy)]