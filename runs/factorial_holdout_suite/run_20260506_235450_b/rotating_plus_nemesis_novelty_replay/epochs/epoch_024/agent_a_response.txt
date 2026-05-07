def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_towards(tx, ty, x, y):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx, dy = step_towards(tx, ty, sx, sy)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # Pick a target we are more likely to reach first (or deny opponent).
    best = None
    best_rx, best_ry = resources[0]
    for rx, ry in resources:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Higher is better: advantage over opponent, then closer to us.
        sc = (opp_d - self_d) * 1000 - self_d
        # Deterministic tie-break: prefer lexicographically smaller (rx, ry).
        if best is None or sc > best or (sc == best and (rx, ry) < (best_rx, best_ry)):
            best = sc
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    # Choose the move that best improves our distance to the target while keeping within valid cells.
    bestm = (0, 0)
    bestv = None
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        self_after = abs(tx - nx) + abs(ty - ny)
        opp_after = abs(tx - ox - 0) + abs(ty - oy - 0)
        # Encourage reducing our distance; small deterrent if move increases distance to target.
        v = (opp_after - self_after, -self_after)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (mx, my)

    # If all candidate moves were blocked (rare), stay.
    return [int(bestm[0]), int(bestm[1])]