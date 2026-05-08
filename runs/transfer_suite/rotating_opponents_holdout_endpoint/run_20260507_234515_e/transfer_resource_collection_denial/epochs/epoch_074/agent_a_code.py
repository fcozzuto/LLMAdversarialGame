def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))

    if not res:
        # No visible resources: head toward opponent-adjacent likely line (reduce chance of getting stuck)
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Dynamic target choice: prefer resources where we can be strictly closer than opponent after our move.
    # Tie-break: prioritize resources already contested (small distance gap), then maximize closeness progress.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate this move against all resources; take the best potential win.
        move_best = -10**18
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            gap = d_opp - d_self  # positive means we move closer than opponent
            # Big bonus if we can become closer (contested theft); smaller bonus for making progress overall.
            v = 200 * gap - 5 * d_self
            # Extra incentive for resources that are close to both (more likely to be collected next).
            if d_opp + d_self > 0:
                v += 12 / (1 + d_opp + d_self)
            # If opponent is already much closer, lower this resource contribution.
            if gap < 0:
                v -= 30 * (-gap)
            if v > move_best:
                move_best = v

        # Prefer safer moves when near obstacles by mild penalty on moving next to obstacles.
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    adj_pen += 1
        move_best -= 1.5 * adj_pen

        if move_best > best_val:
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]