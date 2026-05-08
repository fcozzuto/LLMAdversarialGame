def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick resource where we are relatively closer (arrival earlier), tie-break by closeness to us.
    target = None
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        key = (od - sd, -sd, -manh(ox, oy, rx, ry), rx, ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = target

    # Evaluate 9 moves and choose best deterministic one that is not into obstacle/outside.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        self_d = manh(nx, ny, tx, ty)
        opp_d = manh(ox, oy, tx, ty)
        # Prefer reducing our distance; ensure we keep relative advantage if possible.
        val = (opp_d - self_d, -self_d, -manh(nx, ny, ox, oy), -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]