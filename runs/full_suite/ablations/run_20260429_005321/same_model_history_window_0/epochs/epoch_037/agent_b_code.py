def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    best_val = None
    best_move = [0, 0]

    # Strategy shift: prioritize resources that are closer to us than to opponent (denial),
    # and break ties by preferring resources farther from opponent.
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        candidate = 0.0
        # If standing on a resource, take it immediately.
        on_res = False
        for rx, ry in resources:
            if nx == rx and ny == ry:
                on_res = True
                break
        if on_res:
            return [dx, dy]

        cur_best = -1e9
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            ds = dist(nx, ny, sx, sy)
            d_res_us = dist(nx, ny, rx, ry)
            d_res_op = dist(ox, oy, rx, ry)

            # Base: prefer getting near the resource quickly.
            v = 0.0
            v += 2.5 / (d_res_us + 1)
            # Denial: prefer resources we're closer to than opponent.
            v += 0.8 * (d_res_op - d_res_us)
            # Spread: avoid resources where opponent is already close.
            v += 0.15 * (dist(nx, ny, rx, ry) - dist(ox, oy, rx, ry))
            # Small bias to move toward resources overall.
            v += -0.02 * (d_res_us)

            if v > cur_best:
                cur_best = v

        # Prefer moves that reduce our distance to the best target relative to staying.
        # Deterministic tie-break: slightly prefer moves that change position.
        candidate = cur_best + (0.01 if (dx != 0 or dy != 0) else 0.0)

        if best_val is None or candidate > best_val:
            best_val = candidate
            best_move = [dx, dy]
        elif candidate == best_val:
            # Deterministic tie-break: lexicographic on (dx,dy) to ensure stable output.
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move