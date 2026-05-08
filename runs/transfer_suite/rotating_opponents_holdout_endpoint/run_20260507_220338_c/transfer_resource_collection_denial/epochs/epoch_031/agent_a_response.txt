def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick resource where we can arrive earlier; otherwise pick the least losing one.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (myd == 0, (opd - myd), -myd, -(rx + 31 * ry))  # prioritize advantage, then proximity
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = dist(nx, ny, tx, ty)
        opd2 = dist(ox, oy, tx, ty)
        # Also keep moving "toward the other side" to avoid getting stuck in local pockets.
        center_bias = -abs(nx - (w - 1) // 2) - abs(ny - (h - 1) // 2)
        val = ((opd2 - myd2), -myd2, center_bias)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]