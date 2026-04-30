def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    def resource_score(x, y):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            d = cheb(x, y, tx, ty)
            return 100 - 3 * d
        best = 10**9
        for tx, ty in resources:
            d = cheb(x, y, tx, ty)
            if d < best:
                best = d
        # prefer being closer; slight tie-break toward bottom-right deterministic via (x+y)
        return 200 - 5 * best + 0.01 * (x + 2 * y)

    def opponent_penalty(x, y):
        d = cheb(x, y, ox, oy)
        # if close, strongly discourage; still allow if it also grabs a resource
        return 0 if d >= 3 else 80 - 20 * d

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy  # deterministic: engine keeps us if invalid
        # deterministic evaluation
        v = resource_score(nx, ny) - opponent_penalty(nx, ny) + 0.001 * (nx * 31 + ny)
        # discourage cycling lightly by preferring positions with lower combined parity next
        v += 0.0001 * ((nx + ny) % 2)  # deterministic small bias
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]