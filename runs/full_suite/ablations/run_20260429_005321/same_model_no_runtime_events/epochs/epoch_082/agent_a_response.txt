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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        # Deterministic safe drift: prefer decreasing cheb distance to opponent (force their path)
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Choose resource where we are relatively closer than the opponent; otherwise go nearest to us.
    best_t = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = do - ds  # positive is good
        # Prefer positive rel; among ties, lower ds; then deterministic coordinate tie-break.
        key = (0 if rel > 0 else 1, -rel, ds, rx, ry)
        if best_score is None or key < best_score:
            best_score = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Move one step towards target; avoid illegal cells; deterministic tie-break by (new_dist, dx, dy).
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_dist = cheb(nx, ny, tx, ty)
        # Also discourage stepping adjacent to obstacles when it doesn't improve distance.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        score = (new_dist, adj_obs, abs(dx - (1 if tx > sx else -1 if tx < sx else 0)) + abs(dy - (1 if ty > sy else -1 if ty < sy else 0)))
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return list(best[1]) if best else [0, 0]