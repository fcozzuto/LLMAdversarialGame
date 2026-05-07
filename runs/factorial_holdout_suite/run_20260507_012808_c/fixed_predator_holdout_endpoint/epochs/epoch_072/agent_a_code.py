def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy  # Chebyshev for diagonal moves

    best_ahead = None
    best_any = None
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        ahead = sd <= od
        # Tie-break: prefer larger (od-sd), then smaller sd, then deterministic cell order
        metric = (od - sd, -sd, rx * 100 + ry)
        if ahead:
            if best_ahead is None or metric > best_ahead[0]:
                best_ahead = (metric, (rx, ry))
        if best_any is None or metric > best_any[0]:
            best_any = (metric, (rx, ry))

    target = (best_ahead[1] if best_ahead is not None else best_any[1])
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    # If opponent is very close, prioritize denying by moving to reduce distance to target fastest.
    # Deterministic tie breaks by dx,dy ordering in list.
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = cd(nx, ny, tx, ty)
        # small penalty if closer to opponent (helps denial indirectly by not racing them when tied)
        opp_closer_pen = 0
        if cd(nx, ny, ox, oy) < cd(sx, sy, ox, oy):
            opp_closer_pen = 1
        key = (-d, -opp_closer_pen, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]