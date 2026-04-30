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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def nearest_res_score(x, y):
        # Higher is better
        best = -10**9
        for tx, ty in resources:
            myd = cheb(x, y, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer targets we are closer to; also avoid very far targets.
            val = (opd - myd) * 30 - myd
            if val > best:
                best = val
        return best if resources else -cheb(x, y, ox, oy)

    # If no resources visible, drift to improve space and avoid staying in opponent's Chebyshev neighborhood
    if not resources:
        best_step = None
        best_val = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            dist_opp = cheb(nx, ny, ox, oy)
            # prefer moving away from opponent; tie-break toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = dist_opp * 50 - cheb(nx, ny, cx, cy)
            if val > best_val:
                best_val = val
                best_step = (dx, dy)
        return [best_step[0], best_step[1]] if best_step else [0, 0]

    # Greedy 1-step to maximize "can claim resource next" heuristic
    best_dxdy = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Primary: best resource-claim advantage after moving
        val = nearest_res_score(nx, ny)
        # Secondary: keep some distance from opponent to contest less violently
        val += cheb(nx, ny, ox, oy) * 3
        # Tertiary: deterministic tie-break favoring progress toward closest resource
        if resources:
            tx, ty = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
            val -= cheb(nx, ny, tx, ty) * 0.5
        if val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]