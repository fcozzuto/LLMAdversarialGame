def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_value(nx, ny):
        if resources:
            cx, cy = w // 2, h // 2
            best = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                myd = md(nx, ny, rx, ry)
                opd = md(ox, oy, rx, ry)
                # Primary: win the race to this resource
                race = (opd - myd)
                # Secondary: prefer getting closer to center after capturing
                center = -0.03 * md(rx, ry, cx, cy)
                # Tertiary: slightly prefer resources that are farther from opponent right now
                edge_from_opp = -0.01 * md(rx, ry, ox, oy)
                val = race + center + edge_from_opp
                if val > best:
                    best = val
            return best
        else:
            cx, cy = w // 2, h // 2
            return -md(nx, ny, cx, cy) - 0.01 * md(nx, ny, ox, oy)

    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = step_value(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]
    return best_move