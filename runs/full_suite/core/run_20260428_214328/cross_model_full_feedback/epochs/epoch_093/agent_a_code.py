def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    moves = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    adj8 = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    # If no resources, just stay (still allowed, deterministic).
    if not resources:
        return [0, 0]

    # Deterministically pick a target by minimizing (my_dist - opponent_dist), then by my_dist, then coords.
    best_target = None
    best_key = None
    for r in resources:
        md = dist((sx, sy), r)
        od = dist((ox, oy), r)
        key = (md - od, md, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    tx, ty = best_target

    # Move evaluation: go toward target, avoid obstacles, and slightly block opponent paths to resources.
    def obstacle_pen(nx, ny):
        pen = 0
        for dx, dy in adj8:
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in obstacles:
                pen += 3
        if (nx, ny) in obstacles:
            pen += 1000
        return pen

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_to_t = dist((nx, ny), (tx, ty))
        my_now = dist((sx, sy), (tx, ty))
        step_gain = my_now - my_to_t

        # Contest: prefer states where opponent is relatively farther from the target.
        opp_to_t = dist((ox, oy), (tx, ty))
        # If our move also moves us closer, contest improves; if we move away, contest worsens.
        contest = opp_to_t - my_to_t

        # Small deterministic tie-break: prefer moving that reduces distance to the nearest resource overall.
        nearest_after = None
        for r in resources:
            d = dist((nx, ny), r)
            if nearest_after is None or d < nearest_after[0] or (d == nearest_after[0] and (r[0], r[1]) < nearest_after[1]):
                nearest_after = (d, (r[0], r[1]))
        nearest_d = nearest_after[0]

        val = (-5 * my_to_t) + (2 * step_gain) + (0.7 * contest) - (0.2 * nearest_d) - obstacle_pen(nx, ny) + (0.01 * (nx - sx + 2 * (ny - sy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]