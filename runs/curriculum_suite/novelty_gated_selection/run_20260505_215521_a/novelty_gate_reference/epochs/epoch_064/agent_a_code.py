def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_eval = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        our_best = None
        for rx, ry in resources:
            od = manh(ox, oy, rx, ry)
            nd = manh(nx, ny, rx, ry)
            # Prefer resources where we gain on opponent; also prefer being closer ourselves.
            val = (od - nd) - (0.12 * nd)
            if our_best is None or val > our_best:
                our_best = val

        # If opponent is extremely close to some resource, increase pressure to switch (denial).
        # Approximate by looking at closest opponent distance to any resource.
        opp_closest = None
        for rx, ry in resources:
            d = manh(ox, oy, rx, ry)
            if opp_closest is None or d < opp_closest:
                opp_closest = d

        evalv = our_best
        if opp_closest is not None and opp_closest <= 2:
            # If we also can be close, don't over-switch; otherwise steer away from those contested zones.
            our_min = None
            for rx, ry in resources:
                d = manh(nx, ny, rx, ry)
                if our_min is None or d < our_min:
                    our_min = d
            if our_min is not None and our_min > 2:
                evalv -= (2.0 - 0.5 * opp_closest)

        if best_eval is None or evalv > best_eval:
            best_eval = evalv
            best_move = [dx, dy]

    if best_eval is None:
        return [0, 0]
    return best_move