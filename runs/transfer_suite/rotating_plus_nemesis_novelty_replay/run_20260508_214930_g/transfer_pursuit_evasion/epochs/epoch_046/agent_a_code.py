def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or "pursuer"

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if (sx, sy) in obs:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    dist = abs
    def man(a, b, c, d):  # manhattan
        return dist(a - c) + dist(b - d)

    target_corner = min(corners, key=lambda t: man(ox, oy, t[0], t[1]))
    # If evader heads to nearest corner, pursuer should predict near that direction.
    tx, ty = target_corner

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dcur = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        dnext = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        d_corner = man(nx, ny, tx, ty)
        op_corner = man(ox, oy, tx, ty)

        # pursuer: minimize distance to opponent; also move toward the corner axis only if it helps close.
        # evader: maximize distance from opponent; also move toward farthest corner.
        if "purs" in role.lower():
            # primary: smaller squared distance; secondary: closer to likely corner of opponent
            key = (dnext, d_corner, -op_corner, dx, dy)
        else:
            far_corner = max(corners, key=lambda t: man(sx, sy, t[0], t[1]))
            fx, fy = far_corner
            key = (-dnext, man(nx, ny, fx, fy), dnext, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]