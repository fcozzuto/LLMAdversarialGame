def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for yy in range(h):
            for xx in range(w):
                if valid(xx, yy):
                    sx, sy = xx, yy
                    break
            if valid(sx, sy):
                break

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer resources where we're at least as close as opponent.
        my_pos = (nx, ny)
        opp_pos = (ox, oy)

        if res:
            s = 0.0
            for r in res:
                dm = dist(my_pos, r)
                do = dist(opp_pos, r)
                # Small bonus for becoming the closer collector.
                closer_bonus = 0.0
                if dm <= do:
                    closer_bonus = 2.0
                # Strongly prefer nearer resources.
                s += closer_bonus - 1.3 * dm
            # Keep away from opponent a bit to avoid being trapped.
            s += 0.25 * dist(my_pos, opp_pos)
        else:
            # No resources visible: drift to center while keeping distance.
            s = -0.9 * (abs(nx - cx) + abs(ny - cy)) + 0.3 * dist((nx, ny), (ox, oy))

        # Tie-break deterministically: prefer moves that reduce distance to nearest resource,
        # then smaller lexicographic delta.
        if res:
            nearest_cur = min(dist((sx, sy), r) for r in res)
            nearest_next = min(dist((nx, ny), r) for r in res)
            s += 0.01 * (nearest_cur - nearest_next)
        else:
            nearest_next = 0

        if s > best_score or (s == best_score and (dx, dy) < (best[0], best[1])):
            best_score = s
            best = [dx, dy]

    return [int(best[0]), int(best[1])]