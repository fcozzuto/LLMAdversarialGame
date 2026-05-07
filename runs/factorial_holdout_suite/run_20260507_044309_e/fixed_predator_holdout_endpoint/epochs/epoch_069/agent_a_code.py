def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate the move by the best "lead" it gives on any remaining resource.
        best_lead = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer than opponent
            key = (lead, -sd, rx, ry)
            if best_lead is None or key > best_lead:
                best_lead = key

        if best_lead is None:
            continue
        val = (best_lead[0], best_lead[1])  # (lead, -self_distance)

        # Deterministic tie-break: prefer diagonal moves first, then smaller dx, then smaller dy.
        tie = (0 if dx == 0 or dy == 0 else 1, -abs(dx), -abs(dy), dx, dy)
        cand = (val[0], val[1], tie)

        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]