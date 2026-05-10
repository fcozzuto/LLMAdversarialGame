def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs_cells.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs_cells:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resource_set = set(resources)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_cells:
            if dx != 0 or dy != 0:
                continue
            nx, ny = sx, sy

        if (nx, ny) in resource_set:
            cand_key = (10**9, 0, 0, 0)
        else:
            # Choose move that maximizes winning the next available resource by arrival time.
            best_for_move = None
            for rx, ry in resources:
                if (rx, ry) in obs_cells:
                    continue
                sd = manhattan(nx, ny, rx, ry)
                od = manhattan(ox, oy, rx, ry)
                lead = od - sd  # positive means we can arrive first
                # Small tie-breakers: prefer closer resources and those nearer our current "sweep direction".
                tie_bias = (0 if rx == nx else (1 if rx > nx else -1)) * 0
                row_bias = 0
                if ry == ny:
                    row_bias = 0.25  # help when sweeping horizontally/rows
                elif rx == nx:
                    row_bias = 0.1
                key = (lead, -sd, -row_bias)
                if best_for_move is None or key > best_for_move:
                    best_for_move = key
            cand_key = (best_for_move[0], best_for_move[1], best_for_move[2], nx + 10*ny)

        if best is None or cand_key > best:
            best = cand_key
            best_move = [dx, dy]

    return best_move