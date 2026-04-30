def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    center = (w // 2, h // 2)
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            # Interception-style: prefer resources we can beat the opponent to.
            local_best = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Beat score first; then prefer closer picks.
                score = (opd - myd) * 100 - myd
                # Mild bias away from opponent to reduce immediate contest loss.
                score -= (cheb(nx, ny, ox, oy) * 2)
                if score > local_best:
                    local_best = score
            # If we can't beat anyone, still move toward the best available pick.
            # local_best will be low; add tie-breaker toward center.
            local_best += -cheb(nx, ny, center[0], center[1])
        else:
            # No visible resources: advance to center and reduce distance to opponent-side corner.
            target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else center
            local_best = -cheb(nx, ny, target[0], target[1]) - cheb(nx, ny, center[0], center[1]) * 2

        # Deterministic tie-breaker: lexicographic on (dx,dy) after score.
        if local_best > best_score or (local_best == best_score and (dx, dy) < best_move):
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]