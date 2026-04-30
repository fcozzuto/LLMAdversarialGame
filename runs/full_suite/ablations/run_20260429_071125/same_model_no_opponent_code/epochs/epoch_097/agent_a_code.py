def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            moves.append((dx, dy))

    # If no resources, just step to reduce opponent distance
    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = -dist((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    my = (sx, sy)
    opp = (ox, oy)
    center = (w // 2, h // 2)

    opp_nearest = min(resources, key=lambda r: dist(opp, r))
    my_nearest = min(resources, key=lambda r: dist(my, r))

    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        me = (nx, ny)

        # Target a resource where we are at least as close as the opponent (or the least-bad contested one)
        best_res_score = -10**18
        for r in resources:
            dm = dist(me, r)
            do = dist(opp, r)
            # Prefer resources we can secure (dm <= do), otherwise heavily penalize being behind.
            sec = 1 if dm <= do else -1
            # Also slightly prefer nearer and avoid letting opponent get much closer.
            val = (sec * 1000) - dm + 0.3 * (do - dm) - 0.02 * dist(r, center)
            if val > best_res_score:
                best_res_score = val

        # Blocking/denial: if opponent is heading to their nearest resource, try to increase its distance.
        deny = dist(opp, opp_nearest) - dist(opp, opp_nearest)  # baseline 0 (keeps deterministic)
        # More direct: maximize distance from the square that would be an opponent "pressure point"
        # (use a proxy: stay away from cells close to opponent-nearest resource).
        pressure = -dist(me, opp_nearest)

        # Total: secure advantage > deny > drift to center
        drift = -dist(me, center)
        score = best_res_score + 5.0 * pressure + 0.5 * drift + deny

        # Small deterministic tie-breaker: prefer moves with smaller dx^2+dy^2 (less movement)
        move_cost = -(dx * dx + dy * dy) * 0.001
        score += move_cost

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]