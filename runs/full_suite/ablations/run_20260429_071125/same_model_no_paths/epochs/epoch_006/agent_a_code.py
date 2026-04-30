def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if w <= 0 or h <= 0:
        return [0, 0]

    def norm_pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        return None

    blocked = set()
    for p in obstacles:
        q = norm_pos(p)
        if q is not None:
            blocked.add(q)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    res_pos = []
    for r in resources:
        q = norm_pos(r)
        if q is not None:
            if in_bounds(q[0], q[1]) and q not in blocked:
                res_pos.append(q)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_d_op = abs(sx - ox) + abs(sy - oy)

    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        if res_pos:
            d_to_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res_pos)
            # If we can contest, prefer getting closer than opponent
            d_op_after = abs(nx - ox) + abs(ny - oy)
            val = d_to_res * 100 + max(0, (d_op_after - cur_d_op)) - (1 if d_op_after <= cur_d_op else 0) * 5
        else:
            # No resources: drift toward center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = (abs(nx - cx) + abs(ny - cy)) * 10 - (abs(nx - ox) + abs(ny - oy))

        if val < best[0]:
            best = (val, dx, dy)

    if best[0] == 10**18:
        return [0, 0]
    return [best[1], best[2]]