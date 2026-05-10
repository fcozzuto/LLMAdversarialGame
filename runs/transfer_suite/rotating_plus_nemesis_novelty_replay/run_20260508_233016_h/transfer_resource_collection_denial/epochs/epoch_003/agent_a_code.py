def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    res_set = set(tuple(r) for r in resources)

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Capture immediately if possible
    best_cap = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in res_set and (nx, ny) not in obstacles:
            v = dist2(nx, ny, ox, oy)
            if best_cap is None or v < best_cap[0]:
                best_cap = (v, dx, dy)
    if best_cap:
        return [best_cap[1], best_cap[2]]

    # Pick best target resource to gain on opponent
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    def sign(a):
        return (a > 0) - (a < 0)

    # Evaluate moves by closeness to target and separation from opponent
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v = dist2(nx, ny, ox, oy) * 10 - dist2(nx, ny, tx, ty)
        if best_move is None or v > best_move[0]:
            best_move = (v, dx, dy)

    if best_move:
        return [best_move[1], best_move[2]]
    return [0, 0]