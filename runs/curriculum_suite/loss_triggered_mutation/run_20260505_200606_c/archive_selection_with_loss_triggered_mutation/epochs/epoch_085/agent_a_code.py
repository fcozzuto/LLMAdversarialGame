def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    opp_dist = man(sx, sy, ox, oy)
    best = None  # (score, -newOppDist, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Choose a target resource that we can reach relatively earlier than the opponent.
        best_target_val = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # lower is better: self reach time minus opponent's advantage
            val = sd - 0.9 * od
            if best_target_val is None or val < best_target_val:
                best_target_val = val

        new_opp_dist = man(nx, ny, ox, oy)
        # Also slightly prefer moving away from opponent to reduce stealing in close contests.
        score = best_target_val + 0.06 * (-new_opp_dist)
        key = (score, -new_opp_dist, dx, dy)
        if best is None or key < best[0]:
            best = (key, score)

    if best is None:
        return [0, 0]
    _, dx, dy = best[0], best[0][2], best[0][3]
    return [int(dx), int(dy)]