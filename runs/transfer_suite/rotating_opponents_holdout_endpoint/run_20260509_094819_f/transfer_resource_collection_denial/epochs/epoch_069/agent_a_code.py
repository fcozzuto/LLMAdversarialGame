def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def around_obst(x, y):
        for dx in (-1, 0, 1):
            nx = x + dx
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if (nx, ny) in obs:
                    return 1
        return 0

    if not resources:
        return [0, 0]

    # Precompute resource list in valid int form, deterministic order tie-break by list order.
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            tx, ty = int(p[0]), int(p[1])
            if inb(tx, ty) and (tx, ty) not in obs:
                res.append((tx, ty))
    if not res:
        return [0, 0]

    # Choose move by evaluating next position against best target resource.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine rejects invalid by staying; mimic.
        on_resource = 1 if (nx, ny) in res else 0
        ao = around_obst(nx, ny)
        # Score tries to secure a resource faster than opponent, with slight preference for nearer to self when tie.
        val = -1000000
        for tx, ty in res:
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Higher is better: win the race to the resource, discourage standing near obstacles.
            race = (opp_d - self_d)
            immediate = 1000 if (nx == tx and ny == ty) else 0
            cand = immediate + race * 10 - self_d * 2 - ao * 3
            # Deterministic tie-break: if equal cand, prefer smaller self_d then earlier resource in list.
            if cand > val:
                val = cand
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # deterministic tie-break: smallest |dx|+|dy| then lexicographic on dx,dy
            cb = abs(best_move[0]) + abs(best_move[1])
            cc = abs(dx) + abs(dy)
            if cc < cb or (cc == cb and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]