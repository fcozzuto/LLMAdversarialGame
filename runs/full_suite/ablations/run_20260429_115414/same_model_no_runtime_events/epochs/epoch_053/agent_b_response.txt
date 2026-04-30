def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Move away from opponent while keeping toward our "late" corner
        late = 0
        rem = observation.get("remaining_resource_count", 0)
        try:
            late = int(rem or 0) <= 4
        except:
            late = False
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        if late:
            tx, ty = (w - 1, h - 1) if (sx + sy) < (w - 1 + h - 1) else (0, 0)
        target = (tx, ty)
    else:
        # Race heuristic: prefer resources we can reach sooner than opponent
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer beating opponent; slight preference for closeness
            key = (ds - 1.1 * do, ds + 0.05 * (abs(rx - (w - 1)) + abs(ry - (h - 1))))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose move that reduces distance to target and avoids getting too close to opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_ds = cheb(nx, ny, tx, ty)
        new_do = cheb(nx, ny, ox, oy)
        # If we are close to target, prefer staying on it line; deter approaching opponent too much
        score = (new_ds * 10 + (4 - min(4, new_do)) * 2)
        # Deterministic tie-break: prefer moves with lexicographically smaller (dx,dy)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all neighbors invalid (shouldn't happen), stay
    return [int(best_move[0]), int(best_move[1])]