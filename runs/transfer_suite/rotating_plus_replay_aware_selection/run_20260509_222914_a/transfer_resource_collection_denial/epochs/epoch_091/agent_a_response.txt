def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    best_val = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Choose the best contested resource for the next position (race).
        best_resource_val = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # Primary: maximize how much closer we are than opponent.
            # Secondary: reach sooner, then prefer positions that reduce opponent pressure.
            # Small tie-break: closer in Chebyshev to encourage efficient diagonal.
            cd = sd if sd > 0 else 0
            score = (od - sd, -sd, -od, -(max(abs(nx - rx), abs(ny - ry))), -cd)
            if best_resource_val is None or score > best_resource_val:
                best_resource_val = score

        # Prefer faster global improvement; add slight bias to moves that reduce our distance to nearest resource.
        if best_resource_val is None:
            continue
        near_self = min(md(nx, ny, rx, ry) for rx, ry in resources)
        global_val = (best_resource_val[0], best_resource_val[1], -near_self, dx, dy)
        if best_val is None or global_val > best_val:
            best_val = global_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]