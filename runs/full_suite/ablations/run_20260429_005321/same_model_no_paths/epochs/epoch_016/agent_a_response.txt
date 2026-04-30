def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_adj_pen(x, y):
        p = 0
        for dx, dy in adj:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return -p

    def resource_adv(rx, ry):
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        return (do - ds), ds, do

    # Pick the resource where we have maximal "reach advantage" (opponent farther than us).
    best_res = None
    best_key = None
    for rx, ry in resources:
        adv, ds, do = resource_adv(rx, ry)
        key = (-adv, ds + do, rx, ry)  # deterministic, prefer larger adv then closer overall
        # We encode max-adv by minimizing -adv
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    # If no resources, just drift to reduce obstacle danger (deterministic).
    if best_res is None:
        bx, by = sx, sy
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                val = obstacle_adj_pen(nx, ny)
                if best is None or val > best or (val == best and (dx, dy) < tuple(best_move)):
                    best = val
                    best_move = [dx, dy]
        return best_move

    tx, ty = best_res

    best_val = None
    best_move = [0, 0]
    cur_ds = manh(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns_ds = manh(nx, ny, tx, ty)
        # Prefer moves that make us reach target faster than opponent; add obstacle safety.
        my_adv = (manh(ox, oy, tx, ty) - ns_ds)
        step_eff = -(ns_ds - cur_ds)  # larger when we reduce distance
        val = (my_adv * 1000) + (step_eff * 10) + obstacle_adj_pen(nx, ny)
        # Strongly avoid stepping away if already close
        if ns_ds > cur_ds + 1 and cur_ds <= 2:
            val -= 500
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move