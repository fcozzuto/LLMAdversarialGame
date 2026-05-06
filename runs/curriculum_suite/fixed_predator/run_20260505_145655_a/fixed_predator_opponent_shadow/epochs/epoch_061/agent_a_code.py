def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (x + ox) // 2, (y + oy) // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        if (x + dx, y + dy) in obstacles:
            dx = 0
        if (x, y + dy) in obstacles:
            dy = 0
        return [dx, dy]

    best = None
    best_score = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        score = (d_opp - d_me) * 200 - d_me  # prefer targets we are closer to; then nearer
        tie = (d_opp, tx, ty)
        if best is None or (score, -tie[0], -tie[1], -tie[2]) > best_score:
            best = (tx, ty)
            best_score = (score, -tie[0], -tie[1], -tie[2])

    tx, ty = best
    cx, cy = x, y
    best_m = None
    best_mscore = None

    for dx, dy in deltas:
        nx, ny = cx + dx, cy + dy
        if not in_bounds(nx, ny):
            continue
        # avoid obstacles when possible; allow staying if blocked
        if (nx, ny) in obstacles:
            continue
        d_me_n = abs(tx - nx) + abs(ty - ny)
        d_opp_n = abs(tx - ox) + abs(ty - oy)
        # also directly reduce our distance, and improve "lead" if possible
        mscore = (-d_me_n, (d_me_n - d_opp_n), man((nx, ny), (tx, ty)))
        if best_m is None or mscore > best_mscore:
            best_m = (dx, dy)
            best_mscore = mscore

    if best_m is None:
        # all candidate steps blocked; deterministically step towards target in axis order, allowing staying
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        if (x + dx, y) in obstacles:
            dx = 0
        if (x, y + dy) in obstacles:
            dy = 0
        return [dx, dy]

    return [int(best_m[0]), int(best_m[1])]