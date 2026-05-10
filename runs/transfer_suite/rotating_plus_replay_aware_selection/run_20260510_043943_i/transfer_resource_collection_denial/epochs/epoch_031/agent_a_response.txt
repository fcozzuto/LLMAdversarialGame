def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_adv_score(x, y):
        if not resources:
            return -man(x, y, ox, oy)
        best = -10**9
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; mild preference for closer to us.
            adv = (do - ds) * 10 - ds
            if adv > best:
                best = adv
        return best

    best_val = -10**18
    best_move = [0, 0]

    # Deterministic tie-breaker order already in deltas.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        val = best_adv_score(nx, ny)

        # If no good resource advantage yet, reduce opponent's immediate claim by moving toward "contested" area.
        if resources:
            # Compute our distance to nearest resource and opponent's distance to nearest resource.
            ds0 = 10**9
            do0 = 10**9
            for rx, ry in resources:
                d1 = man(nx, ny, rx, ry)
                if d1 < ds0: ds0 = d1
                d2 = man(ox, oy, rx, ry)
                if d2 < do0: do0 = d2
            val += (do0 - ds0) * 3

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]