def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try: sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    except: pass

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unq = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unq.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        if (nx, ny) in unq: score += 300
        if (nx, ny) in res: score += 120
        if (nx, ny) == (ox, oy): score -= 250
        score += (w + h) - man(nx, ny, ox)  # prefer pushing toward opponent
        score -= man(nx, ny, sx) * 2        # slight preference to move less
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]