def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Predict opponent greedy target: nearest remaining resource (by Manhattan)
    if resources:
        t_rx, t_ry = resources[0]
        best = man(ox, oy, t_rx, t_ry)
        for rx, ry in resources[1:]:
            d = man(ox, oy, rx, ry)
            if d < best:
                best, t_rx, t_ry = d, rx, ry
    else:
        t_rx, t_ry = sx, sy

    # Evaluate moves: grab progress to (possibly) different target,
    # and actively hinder opponent's progress to its predicted target.
    best_move = legal[0]
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        my_t = man(nx, ny, t_rx, t_ry)
        opp_t = man(ox, oy, t_rx, t_ry)

        # If we are already at a resource, strongly prefer staying/continuing.
        my_res_min = 10**9
        opp_res_min = 10**9
        for rx, ry in resources:
            drm = man(nx, ny, rx, ry)
            if drm < my_res_min: my_res_min = drm
            dro = man(ox, oy, rx, ry)
            if dro < opp_res_min: opp_res_min = dro

        # Try to increase opponent's distance from its target (even if our own distance is slightly worse).
        # Also avoid positions that are "too good" for opponent to take next.
        score = 0
        score += 2000 - 50 * my_t  # primary: push towards predicted target
        score += 20 * (opp_t - man(ox, oy, t_rx, t_ry))  # always 0, keep structure

        # Hinder term: for each opponent-possible move, estimate its best approach to the target;
        # choose our move that maximizes that estimate.
        worst_opp_next = -10**9
        for odx, ody in moves:
            onx, ony = ox + odx, oy + ody
            if inside(onx, ony):
                worst_opp_next = max(worst_opp_next, -man(onx, ony, t_rx, t_ry))
        # worst_opp_next is negative manhattan; maximize it => opponent has worse position (larger manhattan)
        score += -30 * (-worst_opp_next)  # equivalently +30*manhattan_avg_est

        # If we can get closer to any resource than opponent, reward.
        if resources:
            score += 80 * (opp_res_min - my_res_min)

        # Mild tie-break: prefer moves that reduce distance to nearest resource (robustness)
        if resources:
            score += -5 * my_res_min

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]