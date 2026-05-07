def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy

    def adjacent_to_obstacle_pen(x, y):
        pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx, ny = x + ax, y + ay
            if (nx, ny) in obstacles: pen += 2
        return pen

    # If on a resource, stay (collect) unless it is blocked (engine would keep anyway).
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = -md(nx, ny, tx, ty) - adjacent_to_obstacle_pen(nx, ny)
            if v > best[1]:
                best = ((dx, dy), v)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    res = [(r[0], r[1]) for r in resources]
    # Evaluate candidate moves by how strongly they win the race to the best resource.
    best_move = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Find best target for self from (nx,ny) considering opponent race.
        best_target_score = -10**18
        for rx, ry in res:
            if (nx == rx and ny == ry):
                self_steps = 0
            else:
                self_steps = md(nx, ny, rx, ry)
            opp_steps = md(ox, oy, rx, ry)
            # Prefer targets where self arrives earlier; otherwise still prefer smaller opp_steps.
            # Also add mild preference for closeness overall.
            win_margin = opp_steps - self_steps
            target_score = 10 * win_margin - 0.5 * self_steps - adjacent_to_obstacle_pen(nx, ny)
            if target_score > best_target_score:
                best_target_score = target_score

        # If move is worse in winning race, avoid; else take the best.
        # Small deterministic tie-breaker: prefer moves that reduce distance to opponent only when races are tied.
        opp_dist = md(nx, ny, ox, oy)
        score = best_target_score - 0.01 * opp_dist
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]