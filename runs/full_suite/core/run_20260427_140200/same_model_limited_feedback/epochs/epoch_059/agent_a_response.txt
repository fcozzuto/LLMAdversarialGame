def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        # Chebyshev distance for diagonal-allowed grid
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    moves = [(dx, dy) for dx, dy in moves if -1 <= dx <= 1 and -1 <= dy <= 1]

    # If standing on a resource, stay (likely to collect)
    if any(r[0] == sx and r[1] == sy for r in resources):
        return [0, 0]

    # Choose best resource: closest to self, then maximize closeness over opponent
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        # Higher priority if we are closer than opponent; deterministic tie-breakers
        key = (d1, -(d2 - d1), abs(rx - sx) + abs(ry - sy), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    rx, ry = best[1]

    # Prefer move that reduces distance to target and keeps path unblocked
    curd = dist((sx, sy), (rx, ry))
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (rx, ry))
        # Score: primary reduce distance, then approach also if opponent competes
        od = dist((ox, oy), (rx, ry))
        cand.append(((nd, -((od - nd) - (od - curd)), abs(nx - rx) + abs(ny - ry), dx, dy), [dx, dy]))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda x: x[0])
    return cand[0][1]