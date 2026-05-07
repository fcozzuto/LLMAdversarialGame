def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = set((a, b) for a, b in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (key, [dx,dy])

    # Find opponent's best immediate target (closest resource to opponent).
    opp_best = None  # (opp_d, rx, ry)
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if opp_best is None or (d, rx, ry) < opp_best:
            opp_best = (d, rx, ry)
    opp_d, opp_tx, opp_ty = opp_best

    # Contest rule: if opponent can reach their closest target at least 1 step sooner, prioritize it.
    contest = False
    my_d_opp = cheb(sx, sy, opp_tx, opp_ty)
    if opp_d < my_d_opp:
        contest = (my_d_opp - opp_d) >= 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacle_set:
            continue

        # Obstacle proximity penalty (discourage running into tight obstacle clusters).
        adj_pen = 0
        for ax, ay in obstacles:
            d0 = cheb(nx, ny, ax, ay)
            if d0 == 0:
                adj_pen += 5
            elif d0 == 1:
                adj_pen += 2
            elif d0 == 2:
                adj_pen += 1

        # Main objective: maximize (opp_dist - self_dist) to a chosen resource.
        if contest:
            # Deterministic: contest opponent's closest target.
            self_d = cheb(nx, ny, opp_tx, opp_ty)
            opp_to = cheb(ox, oy, opp_tx, opp_ty)
            advantage = opp_to - self_d
            # Encourage also closing total distance to prevent oscillation.
            key = (-advantage, self_d, adj_pen, dx, dy)
        else:
            best_adv = None
            best_sd = None
            best_rx = best_ry = None
            for rx, ry in resources:
                self_d = cheb(nx, ny, rx, ry)
                opp_to = cheb(ox, oy, rx, ry)
                advantage = opp_to - self_d
                # Prefer positive advantage; then closer self distance; then deterministic by coords.
                cand = (-(advantage), self_d, rx, ry)
                if best_adv is None or cand < best_adv:
                    best_adv = cand
                    best_sd = self_d
                    best_rx, best_ry = rx, ry
            # Incorporate chosen resource identity implicitly via best_sd/best_rx/best_ry already.
            # Add a small bias to reduce idling: best_sd will naturally reflect movement.
            key = (best_adv[0], best_adv[1], adj_pen, dx, dy)

        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]