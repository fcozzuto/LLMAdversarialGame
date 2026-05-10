def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    resset = set((r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2)
    if (sx, sy) in resset:
        return [0, 0]

    best = None
    best_key = (-10**9, -10**9, 10**9)
    for rx, ry in resset:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise prefer the biggest lead possible.
        key = (od - sd, -sd, od)
        if key[0] > best_key[0] or (key[0] == best_key[0] and (key[1] > best_key[1] or (key[1] == best_key[1] and key[2] < best_key[2]))):
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = (10**9, -10**9, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        nod = dist(ox, oy, tx, ty)
        lead = nod - nd
        step_bias = dx * 3 + dy  # deterministic tie-break
        k = (nd, -lead, step_bias)
        if k < best_move_key:
            best_move_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]