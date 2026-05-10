def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    tx, ty = observation.get("opponent_position", (sx, sy))
    tx, ty = int(tx), int(ty)
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        d = x - a
        if d < 0: d = -d
        e = y - b
        if e < 0: e = -e
        return d + e

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        score = dist(nx, ny, tx, ty)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]