def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            mind = None
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if mind is None or d < mind:
                    mind = d
            key = (mind, (nx - sx) * 0 + (ny - sy) * 0)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    # fallback: move toward opponent
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        mind = abs(nx - ox) + abs(ny - oy)
        key = (mind, -dx, -dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]