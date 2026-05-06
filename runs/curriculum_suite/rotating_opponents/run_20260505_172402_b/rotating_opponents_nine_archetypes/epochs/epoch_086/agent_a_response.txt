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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            else:
                continue
            break

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    resources.sort(key=lambda r: (r[1], r[0]))  # deterministic tie-break

    # If resources exist: pick move that maximizes "competitive advantage" toward the best remaining resource.
    best_move = (0, 0)
    best_val = -10**9

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Consider our best target; penalize if opponent is significantly closer.
            local_best = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # prefer resources we can arrive at sooner (or tie), and close to them.
                val = -ds * 10 - max(0, ds - do) * 8 - (rx + ry) * 0.001
                if do < ds:
                    val -= (ds - do) * 6
                if val > local_best:
                    local_best = val
            if local_best > best_val:
                best_val = local_best
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Fallback (no resources): move to reduce distance to opponent's corner while staying valid.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    tx, ty = target
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]