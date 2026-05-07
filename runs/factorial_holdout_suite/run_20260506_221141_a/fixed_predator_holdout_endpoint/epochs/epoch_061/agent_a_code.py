def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(resources)
    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0: nx = 0
            if nx >= w: nx = w - 1
            if ny < 0: ny = 0
            if ny >= h: ny = h - 1
            if (nx, ny) in obstacles:
                nx, ny = sx, sy
            if (nx, ny) in obstacles:
                nx, ny = sx, sy

            # pick the resource that maximizes our next-step advantage
            chosen = None
            val = None
            for tx, ty in resources:
                self_d = cheb(nx, ny, tx, ty)
                opp_d = cheb(ox, oy, tx, ty)
                if self_d == 0:
                    score = 10**9 + (opp_d * -1) + (tx * -0.001) + (ty * -0.000001)
                else:
                    # maximize (opp sooner) while still preferring reachable targets
                    score = (opp_d - self_d) * 1000 - self_d * 2 + (-(opp_d)) * 0.1 - (tx + ty) * 1e-6
                if val is None or score > val:
                    val = score
                    chosen = (tx, ty)

            if val is None:
                val = -10**18
            # deterministic tie-break by move order and then by chosen target coordinates
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                best_val = val
                best_move = [dx, dy]

    return best_move