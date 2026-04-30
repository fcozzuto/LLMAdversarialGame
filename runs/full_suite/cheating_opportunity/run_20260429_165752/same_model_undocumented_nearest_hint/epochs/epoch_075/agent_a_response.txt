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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def opp_pressure(nx, ny):
        best = -10**9
        # Prefer resources where we are closer than opponent (opp_dist - my_dist is positive).
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            v = opd - myd
            if v > best:
                best = v
        if resources:
            return best
        # If no visible resources, stay central-ish while not giving ground to opponent.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        return -cheb(nx, ny, cx, cy) - 0.25 * cheb(nx, ny, ox, oy)

    best_move = (0, 0)
    best_val = -10**18
    best_dist = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = opp_pressure(nx, ny)
        # Tie-break: move that reduces our distance to the best resource set (or increases distance from opponent if none).
        if resources:
            md = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            tie_dist = md
        else:
            tie_dist = cheb(nx, ny, ox, oy)
            # prefer larger separation => negative in tie compare below
            tie_dist = -tie_dist
        if val > best_val or (val == best_val and tie_dist < best_dist):
            best_val = val
            best_dist = tie_dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]