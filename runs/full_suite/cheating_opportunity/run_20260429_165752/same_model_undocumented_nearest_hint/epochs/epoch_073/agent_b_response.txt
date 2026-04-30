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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift toward center while avoiding opponent pressure.
    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = -10**18
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            dcen = cheb(nx, ny, cx, cy)
            dop = cheb(nx, ny, ox, oy)
            val = (-dcen * 2) + (-dop)
            if val > best:
                best, bestm = val, (dx, dy)
        return [bestm[0], bestm[1]]

    best = -10**18
    bestm = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Evaluate best target advantage from this candidate next position.
        cur_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Primary: try to get to resources where we're ahead (d_opp - d_me).
            adv = d_opp - d_me
            # Secondary: break ties by closer resource and slightly by position away from opponent.
            val = (adv * 50) - (d_me * 3) - (cheb(nx, ny, ox, oy) * 0.5)
            if val > cur_best:
                cur_best = val

        # Small preference to reduce distance to nearest resource overall to avoid stalling.
        near_me = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        val_total = cur_best - near_me * 0.3
        if val_total > best:
            best, bestm = val_total, (dx, dy)

    return [bestm[0], bestm[1]]