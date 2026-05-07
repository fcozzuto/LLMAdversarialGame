def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    step_options = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_gain = -10**9
        best_self_d = 10**9
        best_tid = 0

        for tid, (rx, ry) in enumerate(resources):
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            gain = opp_d - my_d  # positive means we are closer
            if gain > best_gain or (gain == best_gain and my_d < best_self_d) or (gain == best_gain and my_d == best_self_d and tid < best_tid):
                best_gain, best_self_d, best_tid = gain, my_d, tid

        # Secondary objective: prevent opponent from immediately taking many closer resources
        # (approx) compare our best gain to their best gain from their position.
        their_best_gain = -10**9
        for (rx, ry) in resources:
            their_best_gain = max(their_best_gain, dist(sx, sy, rx, ry) - dist(ox, oy, rx, ry))

        # Deterministic preference ordering
        score = (best_gain, -best_self_d, -their_best_gain, dx, dy)
        step_options.append((score, (dx, dy)))

    if not step_options:
        return [0, 0]

    step_options.sort(key=lambda x: x[0], reverse=True)
    return [step_options[0][1][0], step_options[0][1][1]]