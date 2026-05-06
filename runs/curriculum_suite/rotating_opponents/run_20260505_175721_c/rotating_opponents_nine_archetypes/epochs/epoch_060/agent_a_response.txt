def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can reach much earlier than opponent; tie-break deterministically.
            val = (od - sd, -sd, rx, ry)
            if best is None or val > best[0]:
                best = (val, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: intercept denier by moving toward opponent.
        tx, ty = ox, oy

    # Choose among legal moves: maximize reduction in distance to target; small bias to center-ish.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    cur_md = abs(sx - tx) + abs(sy - ty)
    best_mv = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        red = cur_md - nd
        # Bias toward center for stability when reduction ties.
        center_bias = -abs(nx - cx) - abs(ny - cy)
        key = (red, center_bias, -nd, nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]