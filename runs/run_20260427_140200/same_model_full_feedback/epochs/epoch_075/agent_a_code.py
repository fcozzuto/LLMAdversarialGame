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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Safety: if close to opponent, first try to increase distance.
    danger = cheb(sx, sy, ox, oy) <= 2
    if danger:
        best_d = -10**9
        best = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, ox, oy)
                if d > best_d:
                    best_d = d
                    best = [dx, dy]
        return best

    # Choose target: best advantage (opp farther than us) or best denial (minimize our disadvantage).
    if not resources:
        # Deterministic drift toward midpoint-biased opponent flank.
        tx, ty = (ox + 0) // 2, (oy + 0) // 2
        # If target is blocked, drift to nearest legal cell toward it.
        resources = [(tx, ty)]

    best_t = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - md) * 10 - md  # maximize advantage; then minimize my distance
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    # Greedy step toward target, but evaluate locally with advantage.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If stepping closer to target while keeping/creating advantage, prefer it.
            score = (opd - myd) * 10 - myd
            # Small bias: avoid moving onto squares adjacent to opponent if it doesn't help.
            if cheb(nx, ny, ox, oy) <= 1:
                score -= 3
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move