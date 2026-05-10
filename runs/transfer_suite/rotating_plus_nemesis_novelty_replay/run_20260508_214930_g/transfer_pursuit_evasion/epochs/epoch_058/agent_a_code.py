def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))
    if not res:
        res = None

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = -man(nx, ny, ox, oy)
        if res is not None and (nx, ny) in res:
            score += 100000
        # Keep away from obstacles (lightweight, deterministic)
        adj_block = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (nx + ax, ny + ay) in obs:
                adj_block += 1
        score -= adj_block * 5
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    # Fallback: any valid move including stay
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            return [dx, dy]
    return [0, 0]