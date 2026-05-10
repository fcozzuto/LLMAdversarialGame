def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    prefer_feasible = (tr % 2 == 1)

    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        margin = op_d - my_d  # >0 means we arrive no later than opponent
        feasible = 1 if my_d <= op_d else 0
        # Deterministic ranking: prefer feasible captures, then maximize margin, then minimize my distance,
        # then stable coordinate tie-break.
        if prefer_feasible:
            key = (1 - feasible, -margin, my_d, ry, rx)
        else:
            key = (0 if feasible else 1, -margin, my_d, ry, rx)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If direct step would hit an obstacle (rare), try axis move deterministically.
    nx = sx + dx
    ny = sy + dy
    if (nx, ny) in obstacles:
        if dx != 0 and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]

    return [dx, dy]