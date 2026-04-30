def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_rt = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        us = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach no later; then maximize advantage (op-us), then closer overall.
        key = (0 if us <= op else 1, (op - us) * -1, us, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_rt = (rx, ry)

    if best_rt is None:
        return [0, 0]
    tx, ty = best_rt

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return None
        usd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Primary: minimize our distance to target. Secondary: don't fall behind opponent (advantage).
        return (usd, -(opd - usd), nx * 8 + ny)

    best_mv = None
    best_mvkey = None
    for dx, dy in deltas:
        sc = move_score(dx, dy)
        if sc is None:
            continue
        if best_mvkey is None or sc < best_mvkey:
            best_mvkey = sc
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]] if best_mv is not None else [0, 0]