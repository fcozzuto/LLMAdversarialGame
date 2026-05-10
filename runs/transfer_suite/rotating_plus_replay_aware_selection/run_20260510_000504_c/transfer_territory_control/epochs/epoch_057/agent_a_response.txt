def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        targets = resources
    else:
        targets = list(unclaimed) if unclaimed else (list(opp_terr) if opp_terr else [(w - 1, h - 1)])
    # Deterministic progress target: closest, tie by y then x
    bx, by = targets[0]
    bestd = manhattan(sx, sy, bx, by)
    for tx, ty in targets:
        d = manhattan(sx, sy, tx, ty)
        if d < bestd or (d == bestd and (ty < by or (ty == by and tx < bx))):
            bestd, bx, by = d, tx, ty

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def cell_value(x, y):
        if (x, y) in opp_terr:
            return 30
        if (x, y) in unclaimed:
            return 10
        if (x, y) in self_terr:
            return 2
        return 0

    best = None
    best_score = -10**9
    for dx, dy, nx, ny in moves:
        score = 0
        score += cell_value(nx, ny)
        score += -manhattan(nx, ny, bx, by)
        # If moving into new territory, prefer moves that also reduce distance to opponent
        if (nx, ny) in opp_terr or (nx, ny) in unclaimed:
            if opp_terr:
                ox, oy = min(opp_terr, key=lambda p: (manhattan(nx, ny, p[0], p[1]), p[1], p[0]))
                score += -0.5 * manhattan(nx, ny, ox, oy)
            # Small tie-breaker by direction deterministically
        score_tuple = (-(score), dy, dx)  # ensure deterministic ordering on ties
        if best is None or score_tuple < best:
            best = score_tuple
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]