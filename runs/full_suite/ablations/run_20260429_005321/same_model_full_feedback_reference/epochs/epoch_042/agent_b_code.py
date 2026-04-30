def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift toward center while avoiding obstacles
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = resources[0]
        best_val = -10**18
        for x, y in resources:
            sd = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            # Prefer stealing: bigger (od - sd) means we're closer than opponent
            val = (od - sd) * 1000 - sd
            if val > best_val:
                best_val = val
                best = (x, y)
        tx, ty = best

    # Choose move minimizing our distance to target, but penalize letting opponent reach it sooner
    best_move = (0, 0)
    best_cost = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # approximate opponent next distance if it also moves optimally (lower bound via one step)
        oppd_next = max(0, od - 1)
        # If after our move we're not competitive, penalize more heavily
        competit = (myd - oppd_next)
        # Also keep some separation from opponent to reduce contest volatility
        sep = cheb(nx, ny, ox, oy)
        cost = myd * 10 + (0 if competit <= 0 else competit * 50) - min(sep, 3) * 2
        if cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]