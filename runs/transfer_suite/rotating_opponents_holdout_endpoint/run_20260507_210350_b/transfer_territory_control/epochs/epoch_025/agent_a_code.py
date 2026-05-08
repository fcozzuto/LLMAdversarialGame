def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")

    # If resources field is empty, fall back to unclaimed_cells as potential targets
    if not resources:
        resources = to_set("unclaimed_cells")

    opp = observation.get("opponent_position") or [None, None]
    ox = int(opp[0]) if opp[0] is not None else None
    oy = int(opp[1]) if opp[1] is not None else None

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in valid:
            # deterministic tie-break: prefer smaller (dist, -occupiedresource, dx order)
            d2 = min((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry) for (rx, ry) in resources)
            occupied = 1 if (nx, ny) in resources else 0
            key = (d2, -occupied, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    # No resources: try to move toward opponent (to create pressure) while avoiding obstacles
    if ox is not None and oy is not None:
        best = None
        for dx, dy, nx, ny in valid:
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            key = (d2, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    # Otherwise: deterministic stay in place unless blocked
    for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]