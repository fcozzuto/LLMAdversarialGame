def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Bias: if opponent sweep_rows, contest resources by prioritizing those that keep us on different rows
    # (heuristic countermeasure), without hardcoding opponent name.
    sweep_bias = 0.35

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Precompute a simple "our corner direction" score to keep progress deterministic.
    corner_dx = 1 if sx <= w // 2 else -1
    corner_dy = 1 if sy <= h // 2 else -1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        move_val = -0.01 * (dx * dx + dy * dy)  # slight preference for staying close
        # Evaluate best resource we would be heading towards with this move.
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # "Win" term: prefer resources where we are closer than opponent.
            val = (od - sd) * 10.0
            # Distance penalty to finish earlier.
            val -= sd
            # Soft anti-row/anti-column bias: discourage taking same-row as opponent if far behind.
            row_diff = abs(ry - oy)
            if row_diff == 0:
                val -= sweep_bias * (sd + 1)
            # Progress direction (toward our corner) as tie-break to avoid dithering.
            val += 0.02 * ((nx - (0 if corner_dx < 0 else w - 1)) * corner_dx + (ny - (0 if corner_dy < 0 else h - 1)) * corner_dy)
            if val > local_best:
                local_best = val
        move_val += local_best

        if move_val > best_val:
            best_val = move_val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]