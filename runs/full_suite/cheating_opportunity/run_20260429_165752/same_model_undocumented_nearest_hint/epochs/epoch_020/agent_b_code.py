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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = W - 1 - (W - 1 - sx), H - 1 - (H - 1 - sy)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            v = -d
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Strategic change: choose a move that maximizes our "take" advantage against the opponent
    # for the best contested resource, with a small tie-breaker to steer away from the opponent.
    best_move = (0, 0)
    best_val = -10**18
    opp_d_to_resources = None

    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if not legal(nx, ny):
            continue

        # For each resource, compute (opp_dist - our_dist): positive means we are closer.
        best_take = -10**18
        nearest_ours = 10**9
        nearest_opp = 10**9
        for rx, ry in resources:
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_ours < nearest_ours: nearest_ours = d_ours
            if d_opp < nearest_opp: nearest_opp = d_opp
            take = d_opp - d_ours
            if take > best_take:
                best_take = take

        # Encourage going for a contested advantage and, if unclear, increase separation from opponent.
        separation = cheb(nx, ny, ox, oy)
        val = best_take * 1000 - nearest_ours + separation
        if val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]