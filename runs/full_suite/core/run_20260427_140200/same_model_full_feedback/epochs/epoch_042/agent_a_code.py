def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    if not resources:
        # no targets: drift toward center
        cx, cy = w // 2, h // 2
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = abs(nx - cx) + abs(ny - cy)
                if (d, dx, dy) < best:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate moves by how much closer we become than the opponent to the best contested resource.
    best_score = -10**18
    best_move = [0, 0]
    tie = 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # prefer taking a resource, else maximize advantage (opp_d - our_d)
            if (nx, ny) == (rx, ry):
                val = 10**12 - our_d
            else:
                val = (opp_d - our_d) * 1000 - our_d
            if val > move_score:
                move_score = val
        # small deterministic tie-break: prefer smaller our distance to center to reduce loops
        cx, cy = w // 2, h // 2
        tiebreak = md(nx, ny, cx, cy)
        if (move_score, -tiebreak, -dx, -dy) > (best_score, -md(sx, sy, cx, cy), -best_move[0], -best_move[1]):
            best_score = move_score
            best_move = [dx, dy]
    return best_move