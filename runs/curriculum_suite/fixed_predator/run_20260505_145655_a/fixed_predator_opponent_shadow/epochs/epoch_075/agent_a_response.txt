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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Deterministic: drift toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = int(round(cx)), int(round(cy))
        dx, dy = sign(tx - x), sign(ty - y)
        return [dx, dy]

    # Pick best target considering who is closer, with deterministic tie-break
    best = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        lead = d_opp - d_me  # positive => we are closer
        # Encourage advantage and closeness; slight bias to farther-from-opponent (to reduce contest)
        key = (lead * 100000 - d_me * 10 - man(tx, ty, ox, oy), d_opp, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose next move greedily among valid (non-obstacle) moves
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        d_now = man(nx, ny, tx, ty)
        d_cur = man(x, y, tx, ty)
        # Prefer moves that reduce distance to target; add contest pressure and obstacle avoidance already handled
        d_opp_to = man(nx, ny, ox, oy)
        score = (-(d_now - d_cur) * 1000 - d_now * 10 + d_opp_to * 0.02, d_now, d_opp_to, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    # If all neighboring cells were blocked (rare), allow staying
    return best_move if best_move in ([dx, dy] for dx, dy in deltas) else [0, 0]