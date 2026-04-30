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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def opp_best_dist_to(r):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny):
                d = md((nx, ny), r)
                if d < best:
                    best = d
        return best if best != 10**9 else md((ox, oy), r)

    # If no resources, just keep distance from opponent while moving toward center-ish.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -md((nx, ny), (tx, ty)) + 0.3 * md((nx, ny), (ox, oy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = 10**9
        gain = -10**9
        for r in resources:
            dmy = md((nx, ny), r)
            my_d = dmy if dmy < my_d else my_d
            dop = opp_best_dist_to(r)
            # Prefer resources where opponent is further after their best response, and where I'm closer now.
            g = dop - dmy
            gain = g if g > gain else gain
        # Combine: strong preference for "winning" races to resources, then move efficiency.
        val = 2.5 * gain - 0.8 * my_d + 0.05 * md((nx, ny), (ox, oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]