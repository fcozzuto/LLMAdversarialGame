def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if resources:
            md2 = 10**18
            for rx, ry in resources:
                d2 = (rx - nx) * (rx - nx) + (ry - ny) * (ry - ny)
                if d2 < md2:
                    md2 = d2
            dist_score = md2
        else:
            dist_score = -((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny))  # move away if no resources
        # Prefer closer to target (or farther from opponent), then deterministic by direction order
        key = (dist_score, dx, dy)
        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]