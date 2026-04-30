def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: prefer resources we can reach sooner than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Key: prioritize our advantage, then closeness
        key = (0 if ds <= do else 1, ds, cheb(ox, oy, rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # No resources visible: move to center-ish deterministically
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to target; slight penalty for approaching opponent if close
        d_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        opp_pen = 0
        if d_opp <= 1:
            opp_pen = 5  # avoid moving into/near opponent
        # Also avoid stepping "away" from target too much
        score = (d_target, opp_pen, cheb(nx, ny, sx, sy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]