def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    # Pick a deterministic target: unclaimed cell that is good for us and not too close to opponent
    best = None
    best_key = None
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if x == sx and y == sy:
            continue
        if not in_bounds(x, y):
            continue
        if (x, y) in obs_set:
            continue
        key = (dist(ox, oy, x, y), dist(sx, sy, x, y), x, y)
        if best is None or key < best_key:
            best = (x, y)
            best_key = key

    if best is None:
        # Fallback: head toward center but avoid obstacles
        target = (w // 2, h // 2)
    else:
        target = best

    tx, ty = int(target[0]), int(target[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obs_set:
                continue
            # Deterministic tie-breakers: prefer getting closer to target; if equal, prefer farther from opponent
            d_t = abs(tx - nx) + abs(ty - ny)
            d_o = abs(ox - nx) + abs(oy - ny)
            # Also mildly prefer moves that reduce "approach to opponent" by going to cells they are less likely to control
            key = (d_t, -d_o, nx, ny, dx, dy)
            moves.append((key, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda z: z[0])
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]