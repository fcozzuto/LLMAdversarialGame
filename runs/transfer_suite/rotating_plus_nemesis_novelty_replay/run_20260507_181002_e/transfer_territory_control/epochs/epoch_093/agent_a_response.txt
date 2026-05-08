def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = unclaimed if unclaimed else toset(observation.get("resources"))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # deterministic tie-break order: listed moves
    best = None
    best_score = -10**9
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            score = -100000
        else:
            score = 0.0
            if (nx, ny) in unclaimed: score += 6.0
            if (nx, ny) in oppT: score += 4.5
            if (nx, ny) in selfT: score += 1.5
            score += 0.15 * dist(nx, ny, cx, cy) * -1.0  # slightly prefer staying near center
            score += 0.12 * dist(nx, ny, ox, oy)       # prefer farther from opponent to avoid pressure
            # small preference for moving (avoid getting stuck)
            score += 0.03 * (dx != 0 or dy != 0)
        if score > best_score + 1e-12:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]