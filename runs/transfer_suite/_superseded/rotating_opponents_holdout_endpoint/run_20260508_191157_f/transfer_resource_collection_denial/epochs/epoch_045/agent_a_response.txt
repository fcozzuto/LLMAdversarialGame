def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set((x, y) for x, y in obstacles)

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick best target by distance advantage, then deterministic tie-breakers.
    best = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        # Prefer targets where we are closer; if equal, prefer smaller sd, then lexicographic.
        key = (od - sd, -sd, -rx - ry, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Move: deterministic obstacle-aware greedy toward target.
    dx_dir = 0 if tx == sx else (1 if tx > sx else -1)
    dy_dir = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        nd = manh(nx, ny, tx, ty)
        # Small deterministic preference for matching direction to target.
        align = -abs(dx - dx_dir) - abs(dy - dy_dir)
        scored.append((nd, align, nx, ny))
    if scored:
        scored.sort(key=lambda z: (z[0], -z[1], z[2], z[3]))
        _, _, nx, ny = scored[0]
        return [nx - sx, ny - sy]

    # If trapped by obstacles, stay.
    return [0, 0]