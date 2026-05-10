def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    if not resources:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Choose a resource where we have the largest distance advantage; if close, go for proximity.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prioritize: (opponent slower) then (we're closer) then (resource position bias for determinism)
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    d = step_toward(tx, ty)
    dx, dy = d[0], d[1]
    nx, ny = sx + dx, sy + dy

    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
        return [dx, dy]

    # If blocked, pick among valid moves the one that minimizes our distance to target.
    best_mv = [0, 0]
    best_md = None
    for mdx, mdy in moves:
        if mdx == 0 and mdy == 0:
            nx2, ny2 = sx, sy
        else:
            nx2, ny2 = sx + mdx, sy + mdy
        if not (0 <= nx2 < w and 0 <= ny2 < h):
            continue
        if (nx2, ny2) in obstacles:
            continue
        md = cheb(nx2, ny2, tx, ty)
        # Deterministic tie-breaker: smaller dx then smaller dy in scan order
        key = (-md, -abs(mdx), -abs(mdy), mdx, mdy)
        if best_md is None or key > best_md:
            best_md = key
            best_mv = [mdx, mdy]
    return [int(best_mv[0]), int(best_mv[1])]