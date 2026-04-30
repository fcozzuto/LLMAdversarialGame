def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def valid_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid_cell(nx, ny):
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # If only a few resources, bias directly; otherwise use relative pursuit.
    best_move = (0, 0)
    best_val = -10**30

    # Deterministic ordering for tie-breaking
    moves.sort(key=lambda m: (m[0], m[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Big reward for picking up
        if (nx, ny) in res_set:
            val = 10**12
        else:
            val = -dist2(nx, ny, ox, oy) * 0.01  # slight preference to not hand over tempo

            # Pick target: maximize (opp_progress - my_progress) with some tie-break by closeness
            if resources:
                # Evaluate best resource from my move
                local_best = -10**30
                for rx, ry in resources:
                    if (rx, ry) == (nx, ny):
                        continue
                    my_d = dist2(nx, ny, rx, ry)
                    op_d = dist2(ox, oy, rx, ry)
                    # If I can reach sooner, this becomes positive.
                    # Use inverse-style shaping with integers to stay deterministic.
                    gain = (op_d - my_d)
                    # Penalize far-away targets so we don't wander.
                    closeness_pen = my_d
                    score = gain * 1000 - closeness_pen
                    if score > local_best:
                        local_best = score
                val += local_best

        # Also consider blocking: if moving adjacent to opponent reduces their best approach, give small bonus
        # (cheap approximation: prefer decreasing distance to opponent if it would move toward a resource cluster).
        if resources:
            # Opponent distance to nearest resource after our move (approx)
            opp_best = 10**30
            for rx, ry in resources:
                opp_best = min(opp_best, dist2(ox, oy, rx, ry))
            my_best = 10**30
            for rx, ry in resources:
                my_best = min(my_best, dist2(nx, ny, rx, ry))
            val += (opp_best - my_best) * 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]