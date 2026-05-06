def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        # Drift toward center a bit to avoid getting stuck at edges
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                if (d, cheb(nx, ny, ox, oy), dx, dy) < (best[0], best[1], best[2], best[3]):
                    best = (d, cheb(nx, ny, ox, oy), dx, dy)
        return [int(best[2]), int(best[3])]

    if any(r[0] == sx and r[1] == sy for r in resources):
        return [0, 0]

    # Target that maximizes being closer than opponent (denier-aware)
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can secure: larger (od - sd), then smaller sd, then deterministic tie-break
        key = (od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, rx, ry)
        nod = cheb(nx, ny, ox, oy)  # proxy for potential interception/denial pressure
        # Move to reduce our distance to target; also prefer moves that keep opponent farther from us
        val = (-(nsd), nod, -dx, -dy, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [int(dx), int(dy)]

    return best_move