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
    res_set = set(resources)

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        best = -10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -md(nx, ny, cx, cy) - 0.15 * md(nx, ny, ox, oy)
                if val > best:
                    best = val
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    resources_sorted = sorted(resources, key=lambda t: md(sx, sy, t[0], t[1]))
    candidates = resources_sorted[:6] if len(resources_sorted) > 6 else resources_sorted

    best = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
            continue
        if (nx, ny) in res_set:
            return [int(dx), int(dy)]
        my_center = md(nx, ny, cx, cy)
        val = -0.03 * my_center
        for rx, ry in candidates:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if opd == 0 and myd > 0:
                continue
            # Prefer resources we can reach sooner and that keep us ahead of opponent.
            val += (opd - myd) * 2.0 - myd * 0.15
        if val > best:
            best = val
            best_move = (dx, dy)

    # Fallback: drift toward nearest resource if everything rejected (shouldn't happen)
    if best_move == (0, 0):
        target = min(resources, key=lambda t: md(sx, sy, t[0], t[1]))
        tx, ty = target
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [int(best_move[0]), int(best_move[1])]