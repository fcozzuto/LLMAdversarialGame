def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = observation.get("grid_width", 0)
    gh = observation.get("grid_height", 0)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Choose a target resource where we have the advantage (opponent farther)
    if resources:
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = r
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            key = (do - ds, -ds, rx + 3 * ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = sx, sy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if gw and (nx < 0 or nx >= gw):
            continue
        if gh and (ny < 0 or ny >= gh):
            continue
        if (nx, ny) in obs:
            continue
        if resources:
            ds_new = dist2(nx, ny, tx, ty)
            do_sep = dist2(nx, ny, ox, oy)
            val = (-ds_new, do_sep, -dx, -dy)
        else:
            do_sep = dist2(nx, ny, ox, oy)
            val = (do_sep, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move