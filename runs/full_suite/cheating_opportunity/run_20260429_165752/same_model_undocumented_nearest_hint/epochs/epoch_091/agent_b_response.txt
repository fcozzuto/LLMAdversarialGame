def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        # No resources: hold position or move away from opponent if adjacent.
        if cheb(sx, sy, ox, oy) <= 1:
            tx, ty = (sx + (sx - ox)), (sy + (sy - oy))
        else:
            tx, ty = (W - 1) - ox, (H - 1) - oy
        best = (0, 0)
        best_val = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_val:
                best_val = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Target: closest resource by Chebyshev distance; tie-break by distance to opponent (avoid being "intercepted").
    def res_score(r):
        d = cheb(sx, sy, r[0], r[1])
        io = cheb(ox, oy, r[0], r[1])
        # Prefer nearer to us, and slightly prefer being farther from opponent.
        return (d, -io)

    target = min(resources, key=res_score)

    # Evaluate next move: primary is decrease in distance to target; secondary avoid obstacles already handled,
    # tertiary avoid moving too close to opponent.
    best_move = (0, 0)
    best_val = -10**18
    cur_d = cheb(sx, sy, target[0], target[1])
    cur_do = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = cheb(nx, ny, target[0], target[1])
        do = cheb(nx, ny, ox, oy)
        # Prefer moving to target faster; slight preference to keep distance from opponent.
        # Also reward staying put when it's already at same distance level (deterministic tie-break).
        val = (cur_d - d) * 10 + (do - cur_do) * 1 - d * 0.1
        # If d is equal, tie-break by higher do then lexicographic move order via fixed iteration.
        if d == cheb(sx, sy, target[0], target[1]):
            val += do * 0.01
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]