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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(x - ox), -sign(y - oy)]

    best = None
    best_val = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me  # positive means we're ahead
        val = lead * 1000 - d_me - man((tx, ty), (ox, oy)) * 0.001
        if best_val is None or val > best_val:
            best_val = val
            best = (tx, ty)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        d_me2 = abs(tx - nx) + abs(ty - ny)
        d_opp2 = abs(tx - ox) + abs(ty - oy)
        lead2 = d_opp2 - d_me2
        # Encourage improving lead, then getting closer to target; also avoid stepping away.
        progress = (abs(tx - x) + abs(ty - y)) - d_me2
        step_pen = 0
        if (nx, ny) in obstacles:
            step_pen -= 1e9
        sc = lead2 * 1200 + progress * 10 - d_me2 * 0.01 - step_pen
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [dx, dy]