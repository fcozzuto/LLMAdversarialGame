def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_next_dist(px, py, target):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if valid(nx, ny):
                d = md((nx, ny), target)
                if d < best:
                    best = d
        return best if best != 10**9 else md((px, py), target)

    # If no resources visible, just reduce distance to opponent (deterministic fallback)
    if not resources:
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -md((nx, ny), (ox, oy))
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Choose move that maximizes advantage: (opponent best next distance - our next distance) to a target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_next_pos = (nx, ny)
        my_best = -10**9
        # Tie-breakers: prefer closer absolute distance and closer-to-opponent "pressure"
        for r in resources:
            my_d = md(my_next_pos, r)
            opp_d = best_next_dist(ox, oy, r)
            adv = opp_d - my_d
            val = adv * 100 - my_d * 2 - md(my_next_pos, (ox, oy)) * 0.5
            if val > my_best:
                my_best = val
        if best_val is None or my_best > best_val:
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]