def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_score(px, py):
        # Maximize (opponent_dist - my_dist); tie-break: larger my_dist advantage, then nearer, then deterministic.
        best = None
        best_key = None
        for rx, ry in res:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            slack = opd - myd
            key = (slack, -myd, (rx ^ ry) & 1023, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, myd)
        return best_key, best

    # Enumerate moves; avoid obstacles; greedy 1-step lookahead using best_score from each next cell.
    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        key, _ = best_score(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move