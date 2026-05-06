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

    def is_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or is_blocked(nx, ny):
            continue
        val = -10**18
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_me
            v = adv * 1000 - d_me + 0.1 * adv / (1 + d_me)  # deterministic, scale to dominate
            if v > val:
                val = v
        if best_val is None or val > best_val or (val == best_val and (nx, ny) < (x + best_mv[0], y + best_mv[1])):
            best_val = val
            best_mv = (dx, dy)

    if best_val is None:
        return [-sign(ox - x), -sign(oy - y)]
    return [best_mv[0], best_mv[1]]