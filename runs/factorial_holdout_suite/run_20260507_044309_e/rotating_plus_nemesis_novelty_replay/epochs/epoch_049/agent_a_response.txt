def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick resource we can reach earlier, tie-break by being closer and further up/left to be deterministic
    best = None  # (adv, -ds, -rx, -ry, rx, ry)
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        cand = (adv, -ds, -rx, -ry, rx, ry)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]
    _, _, _, _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Prefer moves that increase advantage; if not, prefer closer to target; then reduce opponent-target distance as secondary
        val = ((no - ns), -ns, -no, -abs(nx - tx), -abs(ny - ty), -nx, -ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move