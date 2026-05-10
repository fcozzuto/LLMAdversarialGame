def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = set(tuple(p) for p in (observation.get("resources") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e
    best = None
    best_score = None
    for dx, dy, nx, ny in candidates:
        score = 0
        if (nx, ny) in resources:
            score += 60
        if (nx, ny) in unclaimed:
            score += 35
        if (nx, ny) in self_terr:
            score -= 5
        if (nx, ny) in opp_terr:
            score -= 20
        adj_opp = False
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (nx + ax, ny + ay) in opp_terr:
                adj_opp = True
                break
        if adj_opp:
            score += 25
        score += (w + h) - md(nx, ny, ox, oy)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]