def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in cand:
            v = -(abs(nx - tx) + abs(ny - ty)) - 0.05 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose best target resource; then score candidate moves by improvement over current.
    # Emphasize denial: prefer resources where we can arrive no later than opponent,
    # and slightly penalize moves that move away from top targets.
    cur_best = -10**9
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Primary: win likelihood (opp_dist - self_dist). Secondary: smaller self_dist.
        # Add slight bonus if we can arrive quickly.
        v = (od - sd) * 2.0 - 0.15 * sd + 0.02 * (od)
        if v > cur_best:
            cur_best = v

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in cand:
        bestv = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we're tied or ahead, strongly favor this resource.
            lead = (od - sd)
            v = lead * 2.0 - 0.18 * sd + 0.03 * od
            # Deny pressure: if opponent is closer, being near the resource is less valuable,
            # but still better than wandering; discourage chasing hopeless targets.
            if lead < 0:
                v += lead * 0.6
            if v > bestv:
                bestv = v

        # Prefer moves that improve relative to current best heuristic.
        rel = bestv - cur_best
        # Mild obstacle-adjacent avoidance: don't add extra; just keep deterministic slight bias to stay if equal.
        score = rel * 1000.0 + bestv
        # Deterministic tie-break: prefer smaller dx^2+dy^2, then lexicographic.
        tie = dx * dx + dy * dy
        score_key = (score, -tie, -dx, -dy)
        if best_move is None or score_key > best_score:
            best_score = score_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]