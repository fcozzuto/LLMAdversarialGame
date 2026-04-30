def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []
    res = [tuple(p) for p in resources if (p[0], p[1]) not in obs]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # If no resources visible, drift toward center while avoiding obstacles.
    if not res:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                score = -cheb(nx, ny, cx, cy)
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Avoid enabling opponent: prefer squares that increase (opp_reach - our_reach) to some resource.
        score = 0
        myd_center = cheb(nx, ny, cx, cy)
        score += -myd_center * 1  # mild centralization

        # Soft penalty for moving adjacent to obstacles (deterministic local avoidance).
        adj_obs = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obs:
                adj_obs += 1
        score += -adj_obs * 0.5

        # Main term: choose best target resource by advantage.
        best_t = -10**18
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Big bonus if we can reach before opponent; also account for distance to resource.
            reach_adv = opp_d - our_d
            t = reach_adv * 60 - our_d * 6
            # Extra if opponent is very close to that resource (deny it).
            if opp_d == 0:
                t -= 500
            elif opp_d == 1:
                t -= 120
            best_t = t if t > best_t else best_t
        score += best_t

        # If we are currently adjacent to a resource, prioritize that directly.
        cur_best = 0
        for rx, ry in res:
            if cheb(sx, sy, rx, ry) == 0:
                cur_best += 1
        score += cur_best * 30

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]