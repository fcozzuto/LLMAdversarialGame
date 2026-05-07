def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0),(0,0),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    res_list = [tuple(r) for r in resources]
    if (sx, sy) in set(res_list):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_value(px, py):
        best = None
        for tx, ty in res_list:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(px, py, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer resources where we are closer; otherwise still move toward them if denial is likely.
            v = (opd - myd) * 10 - myd
            # Small bias toward nearer overall resources to avoid oscillation.
            v2 = -myd
            cand = (v, v2, -tx, -ty)
            if best is None or cand > best:
                best = cand
        if best is None:
            return (-10**9, 0, 0, 0)
        return best

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_value(nx, ny)
        # If we step onto a resource, strongly prefer it.
        if (nx, ny) in set(res_list):
            v = (v[0] + 10**6, v[1], v[2], v[3])
        if best_score is None or v > best_score:
            best_score = v
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]