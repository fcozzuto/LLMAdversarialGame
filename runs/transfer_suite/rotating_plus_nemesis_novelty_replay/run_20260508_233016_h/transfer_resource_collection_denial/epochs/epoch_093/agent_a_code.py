def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = {tuple(p) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    # Choose resource that we are most likely to reach first; if tied, prefer closer.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        slack = op_d - my_d  # positive => we are closer
        # Encourage taking contested targets a bit earlier.
        key = (-slack, my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # If we are not closer, do a deterministic "denial" interception:
    # aim for a cell on our way that reduces opponent's advantage.
    my_d0 = cheb(sx, sy, tx, ty)
    op_d0 = cheb(ox, oy, tx, ty)

    # Candidate moves scored by: distance to target + denial vs opponent progress.
    best_move = (0, 0)
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_d = cheb(nx, ny, tx, ty)

        # Denial term: if opponent is closer, bias to reduce our slowness and their proximity simultaneously.
        op_near = cheb(ox, oy, tx, ty)
        # Estimate our new "slack" (how much closer we are than opponent if we continued optimally).
        slack_after = op_near - my_d

        # Extra incentive: when contested (we not closer), also prefer moving to reduce max-axis distance between our pos and opponent toward target direction.
        contest = 1 if my_d0 > op_d0 else 0
        if contest:
            # Move direction toward target; if we step along that direction, we "cut in".
            dirx = 0 if tx == nx else (1 if tx > nx else -1)
            diry = 0 if ty == ny else (1 if ty > ny else -1)
            intercept = 0 if (dirx == 0 and diry == 0) else cheb(nx, ny, ox, oy)
            # Lower intercept is better; also reward non-increasing distance to target.
            denial = intercept
        else:
            denial = 0

        # Deterministic combined objective: smaller is better.
        # Primary: best expected order (via -slack); Secondary: reach target quickly; Tertiary: avoid staying if possible.
        stay_pen = 0 if (dx != 0 or dy != 0) else 0.05
        val = (-(slack_after), my_d, denial, stay_pen, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]