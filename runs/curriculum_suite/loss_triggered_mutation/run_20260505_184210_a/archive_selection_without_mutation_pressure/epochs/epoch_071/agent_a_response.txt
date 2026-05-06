def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    if not resources:
        # Defensive: move to reduce distance to opponent (interrupt sweep/contest space)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, ox, oy)
            key = (-d, dx, dy)  # deterministically maximize -d
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    # Predict opponent's likely target: closest remaining resource
    opp_target = min(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))

    best_move = legal[0]
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        # Compete for resources: maximize (opp_dist - my_dist) race advantage
        my_d_to_opp_t = man(nx, ny, opp_target[0], opp_target[1])
        opp_d_to_opp_t = man(ox, oy, opp_target[0], opp_target[1])
        race = opp_d_to_opp_t - my_d_to_opp_t

        nearest_my = min(resources, key=lambda r: (man(nx, ny, r[0], r[1]), r[0], r[1]))
        my_near_d = man(nx, ny, nearest_my[0], nearest_my[1])
        opp_near_d = min(man(ox, oy, r[0], r[1]) for r in resources)

        # Also consider best race over all resources (one-step lookahead)
        best_race_all = -10**9
        for rx, ry in resources:
            best_race_all = max(best_race_all, man(ox, oy, rx, ry) - man(nx, ny, rx, ry))

        # If we're behind on opponent's predicted target, still grab any race win elsewhere
        val = 6 * best_race_all + 2 * race + 0.25 * (opp_near_d - my_near_d) - 0.01 * my_near_d
        key = (-(val), dx, dy)
        cur_key = (-(best_val), best_move[0], best_move[1])
        if best_val == -10**18 or key < cur_key:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]