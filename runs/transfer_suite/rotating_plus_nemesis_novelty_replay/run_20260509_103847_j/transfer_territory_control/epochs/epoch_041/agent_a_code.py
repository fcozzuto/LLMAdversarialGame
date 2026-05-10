def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [0, 0])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    sc = observation.get("scores") or {}
    my_sc = sc.get("self", sc.get("me", 0)) if isinstance(sc, dict) else 0
    op_sc = sc.get("opponent", sc.get("opp", 0)) if isinstance(sc, dict) else 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        # target nearest unclaimed (deterministic)
        best_t = None
        best_d = 10**9
        for tx, ty in unclaimed:
            d = dist(sx, sy, tx, ty)
            if d < best_d or (d == best_d and (tx, ty) < best_t):
                best_d, best_t = d, (tx, ty)
        tx, ty = best_t
        chase = True
    else:
        tx, ty = ox, oy
        chase = my_sc <= op_sc

    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        d_to_t = dist(nx, ny, tx, ty)
        d_from_op = dist(nx, ny, ox, oy)
        if chase:
            # minimize distance to target; prefer farther from opponent on ties
            key = (d_to_t, -d_from_op, dx, dy)
        else:
            # defend: maximize distance from opponent; among them, move toward target
            key = (-d_from_op, d_to_t, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]