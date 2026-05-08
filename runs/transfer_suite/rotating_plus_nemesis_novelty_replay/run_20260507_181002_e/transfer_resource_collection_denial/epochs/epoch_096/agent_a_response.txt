def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score(x, y, px, py):
        sd = man(x, y, px, py)
        od = man(x, y, ox, oy)
        return (od - sd, -sd)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = (-10**18, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # One-step lookahead: assume we will chase the best-scoring resource from (nx, ny).
        best_cell = None
        best_cell_val = (-10**18, -10**18)
        for rx, ry in resources:
            v = cell_score(rx, ry, nx, ny)
            if v > best_cell_val:
                best_cell_val = v
                best_cell = (rx, ry)
        # Prefer reducing distance to the chosen best cell.
        bx, by = best_cell
        dist_to_best = man(bx, by, nx, ny)
        v2 = (best_cell_val[0], best_cell_val[1] - dist_to_best)
        if v2 > best_val:
            best_val = v2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]