def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_dxdy = (0, 0)
        best_score = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Score resources by advantage: closer to us, farther from opponent.
            local_best = 10**18
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                # Prefer capturing/holding: our distance minus half of opponent lead.
                score = d1 - (d2 - d1) * 0.5
                if score < local_best:
                    local_best = score
            # Small tie-break: prefer moves that reduce our nearest distance.
            nearest_now = local_best
            if nearest_now < best_score - 1e-12:
                best_score = nearest_now
                best_dxdy = (dx, dy)
        return [int(best_dxdy[0]), int(best_dxdy[1])]

    # No resources visible: drift toward opponent-side corner to stay in contention.
    tx = w - 1 if ox < w // 2 else 0
    ty = h - 1 if oy < h // 2 else 0
    best = 10**18
    best_dxdy = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best:
            best = d
            best_dxdy = (dx, dy)
    return [int(best_dxdy[0]), int(best_dxdy[1])]