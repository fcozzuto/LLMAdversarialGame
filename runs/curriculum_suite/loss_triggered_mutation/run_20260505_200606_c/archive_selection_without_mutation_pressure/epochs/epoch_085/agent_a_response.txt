def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    res_in = observation.get("resources") or []
    obs_in = observation.get("obstacles") or []

    obstacles = set()
    for p in obs_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in res_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a single strategic target: prefer resources where we are (or can become) relatively ahead.
    best_target = None
    best_tval = -10**18
    for (rx, ry) in resources:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Being ahead is hugely valuable; also avoid far resources.
        tval = (d_opp - d_self) * 2000 - d_self
        if d_self == 0:
            tval += 10**7
        if tval > best_tval:
            best_tval = tval
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_self = man(nx, ny, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        # Move toward target, but also keep distance from opponent to reduce contest interference.
        # If opponent is closer, we still move toward the target but with an extra contest-avoidance term.
        contest = -man(nx, ny, ox, oy) * (2 if d_opp < d_self else 1)
        val = (d_opp - d_self) * 2500 - d_self + contest
        if d_self == 0:
            val += 10**7
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]