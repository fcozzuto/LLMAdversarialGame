def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in cand:
            v = -kdist(nx, ny, int(tx), int(ty))
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in cand:
        # Prefer moves that get closer to a resource while denying the opponent.
        # Choose the resource that maximizes (opp_dist - self_dist) for this candidate.
        best_gap = -10**9
        best_dself = 10**9
        tie_x = tie_y = 0
        for rx, ry in resources:
            ds = kdist(nx, ny, rx, ry)
            do = kdist(ox, oy, rx, ry)
            gap = do - ds
            if gap > best_gap or (gap == best_gap and (ds < best_dself or (ds == best_dself and (rx, ry) < (tie_x, tie_y)))):
                best_gap, best_dself, tie_x, tie_y = gap, ds, rx, ry

        # Penalty if we step adjacent to obstacles too much (soft trap-avoidance).
        adj_obs = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_obs += 1

        # Bonus for moving toward that target and slightly toward increasing secured advantage.
        opp_now = kdist(ox, oy, tie_x, tie_y)
        self_now = best_dself
        v = 10 * best_gap - 3 * self_now + (opp_now - self_now) - 0.8 * adj_obs
        # Secondary tiebreak: prefer moves that reduce distance to opponent (interference) only if gap not strong.
        if best_gap <= 0:
            v -= 0.2 * kdist(nx, ny, ox, oy)

        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]