def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev

    target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach sooner; tie-break by absolute closeness then coordinates.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)
    if target is None:
        return [0, 0]
    tx, ty = target

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            new_d = dist((nx, ny), (tx, ty))
            # Small bias to avoid standing still unless already optimal
            stand_pen = 0 if (dx != 0 or dy != 0) else 0.01
            # Also mildly discourage moving away from resources we should contest
            do = dist((ox, oy), (tx, ty))
            key = (new_d - do, new_d, stand_pen, nx, ny)
            candidates.append((key, [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: z[0])
    return candidates[0][1]