def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    dirs = [(dx, dy) for dy in dys for dx in dxs]  # deterministic order

    def man(a, b, c, d):
        v = a - c
        if v < 0: v = -v
        t = b - d
        if t < 0: t = -t
        return v + t

    if resources and (observation.get("remaining_resource_count", len(resources)) != 0):
        tx, ty = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        # If no resources, head toward opponent to gain points/pressure; else center.
        # Use opponent unless it is out of bounds (shouldn't be).
        if inb(ox, oy):
            tx, ty = ox, oy
        else:
            tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = man(nx, ny, tx, ty)
        # Prefer moves that would land on a resource (if any), and break ties deterministically
        if resources:
            if (nx, ny) in obs:
                pass
            else:
                if (nx, ny) == (tx, ty):
                    v -= 10
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]