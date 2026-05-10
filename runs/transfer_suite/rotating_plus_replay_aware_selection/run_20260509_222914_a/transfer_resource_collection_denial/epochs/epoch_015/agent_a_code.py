def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        if abs(tx - x) >= abs(ty - y):
            return [dx, 0] if dy != 0 else [dx, dy]
        return [0, dy]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (-10**9, 10**9, 10**9)
    best_move = [0, 0]

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue

        # Evaluate move by the best resource "race" we can create this turn.
        local_best = (-10**9, 10**9, 10**9)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd  # positive means we are closer than opponent to this resource
            # Parity tweak to reduce ties; deterministic and cheap.
            parity = ((nx + ny) & 1) ^ ((rx + ry) & 1)
            val = gap * 10 - parity
            # Prefer resources we can actually reach sooner (smaller sd).
            cand = (val, sd, man(nx, ny, w // 2, h // 2))
            if cand > local_best:
                local_best = cand

        # Prefer move that gives best local_best; then smallest own distance to center (stability).
        if local_best > best:
            best = local_best
            best_move = [dx0, dy0]

    return [int(best_move[0]), int(best_move[1])]