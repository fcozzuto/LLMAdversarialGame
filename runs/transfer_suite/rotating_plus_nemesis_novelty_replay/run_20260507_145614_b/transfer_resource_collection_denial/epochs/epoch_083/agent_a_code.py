def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def on_res(x, y):
        for rx, ry in resources:
            if rx == x and ry == y:
                return True
        return False

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    if on_res(sx, sy):
        return [0, 0]

    # Prefer resources we can reach strictly earlier; otherwise choose a target that minimizes our disadvantage.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd < od:
            key = (0, sd, od, abs(rx - ox) + abs(ry - oy))
        else:
            key = (1, sd - od, sd, abs(rx - ox) + abs(ry - oy))
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]
    # If opponent is very close to our target, move one step to reduce their arrival even if not strictly on the target.
    if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty) and (turns_remaining % 2 == 0):
        # Shadow point: step toward the target by one; this keeps pressure deterministic.
        tx = sx + (1 if tx > sx else -1 if tx < sx else 0)
        ty = sy + (1 if ty > sy else -1 if ty < sy else 0)

    dx_raw = 0 if sx == tx else (1 if tx > sx else -1)
    dy_raw = 0 if sy == ty else (1 if ty > sy else -1)

    # Deterministic obstacle-aware move selection: try best delta then alternatives.
    deltas = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            # prefer moves that reduce our cheb distance to (tx,ty); tie-break also reduces opponent's distance
            deltas.append((cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), abs(dx - dx_raw) + abs(dy - dy_raw), [dx, dy], (nx, ny)))
    deltas.sort(key=lambda z: (z[0], z[2], z[1]))
    for _, _, _, mv, (nx, ny) in deltas:
        if (nx, ny) not in obstacles:
            return mv
    return [0, 0]