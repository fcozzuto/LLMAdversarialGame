def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18

    # Target resources: prioritize those closer to opponent (denier pressure), but compete with timing.
    scored_resources = []
    for rx, ry in resources:
        d_opp = dist(ox, oy, rx, ry)
        scored_resources.append((d_opp, rx, ry))
    scored_resources.sort(key=lambda t: (t[0], t[1], t[2]))
    top_targets = scored_resources[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        val = 0
        # For each likely target, estimate advantage by time-to-reach.
        # Also include denial: prefer reducing opponent's best distance.
        opp_best_before = 10**9
        opp_best_after = 10**9
        for _, rx, ry in top_targets:
            opp_best_before = min(opp_best_before, dist(ox, oy, rx, ry))
            opp_best_after = min(opp_best_after, dist(ox, oy, rx, ry))  # static opponent (same each turn)
            d_us = dist(nx, ny, rx, ry)
            d_them = dist(ox, oy, rx, ry)
            # If we can arrive earlier, reward strongly; otherwise slightly discourage.
            time_adv = d_them - d_us
            val += 20 * (1 if time_adv > 0 else 0) * (time_adv + 1)
            val += -d_us * 1.2
            # If we can reach very fast, extra.
            val += 10 / (1 + d_us)

        # Denial pressure: choose moves that move toward the opponent's nearest target.
        d_opp_near = min(dist(ox, oy, rx, ry) for _, rx, ry in top_targets)
        closest_us_to_opp_target = min(dist(nx, ny, rx, ry) for _, rx, ry in top_targets)
        val += 2.5 * (d_opp_near - closest_us_to_opp_target)

        # Mild obstacle-aware tie-break: prefer staying within bounds naturally already.
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]