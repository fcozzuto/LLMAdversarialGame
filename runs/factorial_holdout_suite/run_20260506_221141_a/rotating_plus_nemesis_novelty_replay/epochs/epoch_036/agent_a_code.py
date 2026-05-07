def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources_in = observation.get("resources") or []
    resources = []
    for r in resources_in:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh): 
            continue
        if (nx, ny) in obs:
            continue

        # Small obstacle proximity penalty to reduce getting stalled.
        prox_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    prox_pen += 1

        self_best = 10**9
        opp_best = 0
        dist_term = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            # Encourage securing a resource before opponent; also value nearer finish.
            gap = od - sd
            # Use a composite to avoid purely greedy when a tie.
            score_here = (gap * 100) - sd - (abs(rx - nx) + abs(ry - ny)) - (sd > 2 and (od <= sd + 0))
            if score_here > dist_term:
                dist_term = score_here
                self_best = sd
                opp_best = od

        # Tie-break: prefer lower self distance and larger gap; penalize obstacles near landing.
        key_score = dist_term + (opp_best - self_best) * 5 - prox_pen * 3
        if key_score > best_score:
            best_score = key_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]