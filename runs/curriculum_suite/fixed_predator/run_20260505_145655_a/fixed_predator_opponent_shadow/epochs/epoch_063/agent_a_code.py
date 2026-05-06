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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Choose a resource we can realistically contest; prioritize positive lead (opp far / we near)
    best = None
    best_key = None
    for tx, ty in resources:
        d_me = dist((tx, ty), (x, y))
        d_opp = dist((tx, ty), (ox, oy))
        lead = d_opp - d_me  # positive means we are closer
        # Key: maximize lead, then minimize our distance, then lexicographic
        key = (lead, -d_me, -abs(tx - ox) - abs(ty - oy), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # If contested badly, add a slight "shadow cut": move to reduce our distance to chosen target more than opponent.
    want_dx = 0 if tx == x else (1 if tx > x else -1)
    want_dy = 0 if ty == y else (1 if ty > y else -1)

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me2 = dist((tx, ty), (nx, ny))
        d_me0 = dist((tx, ty), (x, y))
        d_opp2 = dist((tx, ty), (ox, oy))
        # Step quality: reduce our distance; prefer matching direction to target; also increase lead vs opponent.
        improve = d_me0 - d_me2
        dir_align = -((dx - want_dx) * (dx - want_dx) + (dy - want_dy) * (dy - want_dy))
        # Secondary: avoid getting closer to opponent when we're not gaining much (deterministic stab).
        opp_pressure = -dist((ox, oy), (nx, ny))
        key = (improve, dir_align, lead if False else 0, opp_pressure, -nx, -ny)
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    dx, dy = best_step
    # Always return valid integers in {-1,0,1}
    if dx not in (-1, 0, 1): dx = 0
    if dy not in (-1, 0, 1): dy = 0
    return [dx, dy]