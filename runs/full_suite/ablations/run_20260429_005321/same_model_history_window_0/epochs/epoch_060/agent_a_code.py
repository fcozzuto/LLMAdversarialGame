def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we are relatively closer than the opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer: large advantage, then smaller our distance, then farther opponent distance.
        key = (do - ds, -ds, do, - (rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        # After move, reassess opponent pressure to avoid repeatedly losing tempo.
        do = dist((ox, oy), (tx, ty))
        adv = do - ns
        # Prefer decreasing distance and gaining advantage; break ties toward center-ish.
        key = (adv, -ns, -abs(nx - w / 2) - abs(ny - h / 2), -(dx * dx + dy * dy))
        candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]