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
    if not resources:
        return [0, 0]

    def cdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_mv = (0, 0)
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            # Evaluate by the best contested resource from the new position
            # Score favors being earlier than opponent; tie-breaker: shorter self time; then farther opponent time.
            local_best = None
            for rx, ry in resources:
                st = cdist(nx, ny, rx, ry)
                ot = cdist(ox, oy, rx, ry)
                score = (ot - st, -st, ot)
                if local_best is None or score > local_best:
                    local_best = score
            # Small diversification: prefer moves that also move toward the dominant target direction
            if local_best is None:
                continue
            if best_score is None or local_best > best_score:
                best_score = local_best
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]