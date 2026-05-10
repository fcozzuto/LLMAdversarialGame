def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        unclaimed = observation.get("resources") or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Pick a target that is far from opponent (to resist center-chasing), but not too far from center.
    best_t = None
    best_key = None
    for p in unclaimed:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if not inside(x, y):
            continue
        d_opp = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        d_ctr = (x - cx) * (x - cx) + (y - cy) * (y - cy)
        # maximize d_opp, minimize d_ctr (with a small weight)
        key = (-d_opp + (d_ctr * 0.3), x, y)  # minimize this key
        if best_key is None or key < best_key:
            best_key = key
            best_t = (x, y)

    if best_t is None:
        best_t = (cx, cy)

    tx, ty = best_t

    # Choose next move that heads toward target while avoiding obstacles.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer smaller distance to target, and also keep distance from opponent.
        val = (d_t - 0.05 * d_o, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]