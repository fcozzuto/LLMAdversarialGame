def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose best target: minimize our distance and maximize advantage over opponent.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        # No accessible resources: move toward center deterministically.
        tx, ty = w // 2, h // 2
        tx = clamp(tx, 0, w - 1)
        ty = clamp(ty, 0, h - 1)
        dxs, dys = tx - sx, ty - sy
        step = (0 if dxs == 0 else (1 if dxs > 0 else -1), 0 if dys == 0 else (1 if dys > 0 else -1))
        nx, ny = sx + step[0], sy + step[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [step[0], step[1]]
        return [0, 0]

    _, (tx, ty) = best
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try moves ordered deterministically: diagonal, then axial, then stay.
    candidates = []
    for dx, dy in [(desired_dx, desired_dy), (desired_dx, 0), (0, desired_dy), (desired_dx, -desired_dy), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    # Pick candidate that minimizes our cheb distance to target, then tie-break by dx,dy.
    best_move = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        score = (cheb(nx, ny, tx, ty), dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, (dx, dy))
    return [best_move[1][0], best_move[1][1]]