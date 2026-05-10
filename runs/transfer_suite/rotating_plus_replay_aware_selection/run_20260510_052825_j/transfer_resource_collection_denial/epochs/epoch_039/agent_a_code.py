def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obstacles]
    if not valid:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-way step

    target = None
    best = None
    for rx, ry in valid:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach no later than opponent; then maximize arrival margin.
        # Deterministic tie-break by coordinates.
        key = (od - sd, -sd, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    tx, ty = target

    if sx == tx and sy == ty:
        return [0, 0]

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_sd = dist((sx, sy), (tx, ty))
    best_move = [0, 0]
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Prefer moves that reduce distance; if equal, keep progressing along the dominant axis toward target.
        # Also slightly avoid moves that would bring us close to opponent (stay-at-safe).
        opp_d_after = dist((ox, oy), (nx, ny))
        k = (-(nd - cur_sd), -nd, (abs((nx - tx)) <= abs((sx - tx))), -opp_d_after, -dx, -dy)
        if best_key is None or k > best_key:
            best_key = k
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]