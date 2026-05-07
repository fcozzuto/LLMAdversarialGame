def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    blocked = obstacles
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in blocked:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds
        key = (adv, -ds, -abs(rx - sx) - abs(ry - sy))
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        ds = dist((nx, ny), (tx, ty))
        # Prefer states that improve our distance to target; break ties by also reducing opponent distance.
        do = dist((ox, oy), (tx, ty))
        score = (-ds, -(do - ds), -(abs(nx - tx) + abs(ny - ty)))
        candidates.append((score, (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [candidates[0][1][0], candidates[0][1][1]]