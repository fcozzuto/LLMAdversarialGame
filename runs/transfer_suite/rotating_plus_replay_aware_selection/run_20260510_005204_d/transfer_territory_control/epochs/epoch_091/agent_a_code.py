def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                unclaimed.append((x, y))

    if resources:
        target = min(resources, key=lambda t: (t[0] - sx) ** 2 + (t[1] - sy) ** 2)
    elif unclaimed:
        target = min(unclaimed, key=lambda t: (t[0] - sx) ** 2 + (t[1] - sy) ** 2)
    else:
        target = (ox, oy)

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    bestd = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            d = (nx - target[0]) ** 2 + (ny - target[1]) ** 2
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0]