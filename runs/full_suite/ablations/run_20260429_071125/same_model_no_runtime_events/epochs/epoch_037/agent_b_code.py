def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if resources:
        best_t = None
        best_k = None
        for tx, ty in resources:
            myd = king_dist(sx, sy, tx, ty)
            opd = king_dist(ox, oy, tx, ty)
            # Prefer resources that are nearer to us but farther from opponent.
            k = myd * 10 - opd * 7
            if best_k is None or k < best_k or (k == best_k and (tx + ty) < (best_t[0] + best_t[1])):
                best_k = k
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd_to_t = king_dist(nx, ny, tx, ty)
        nd_to_o = king_dist(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) in obstacles else 0  # should never happen due to valid()
        # Heuristic: get to target, keep distance from opponent, strongly reward landing on a resource.
        res_bonus = 0
        if resources and (nx, ny) in set(resources):
            res_bonus = 120
        val = (-nd_to_t * 12) + (nd_to_o * 5) + res_bonus
        # If resources exist, slightly penalize moving away from target.
        if resources:
            cur_d = king_dist(sx, sy, tx, ty)
            if nd_to_t > cur_d:
                val -= 6
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]