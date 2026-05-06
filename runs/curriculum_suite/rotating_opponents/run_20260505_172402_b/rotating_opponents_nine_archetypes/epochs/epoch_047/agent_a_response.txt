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

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    if not resources:
        candidates = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]
        tx, ty = candidates[0]
        best = (10**9, 10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, cheb(nx, ny, ox, oy), (dx, dy)) < (best[0], best[1], best[2]):
                best = (d, cheb(nx, ny, ox, oy), (dx, dy))
        return list(best[2]) if best[2] is not None else [0, 0]

    # Choose resource where we are relatively closer than opponent (deterministic tie-breakers)
    best_target = None
    best_key = None
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # minimize (self-opp), then minimize self distance, then deterministic coordinate order
        key = (d_self - d_opp, d_self, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Greedy step towards target with local obstacle avoidance; tie-break away from opponent a bit
    best_move = None
    best = (10**9, 10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; if tie, prefer increasing distance to opponent; then deterministic order
        key = (d_t, -d_o, dx * dx + dy * dy)
        if key < best:
            best = key
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]