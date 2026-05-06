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

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    me = (x, y)
    opp = (ox, oy)

    # Choose a target that maximizes how much closer we are than opponent (deterministic tie-breaks)
    best = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        key = (-(lead * 1000 - d_me + 0.01 * d_opp), d_me, d_opp, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # One-step evaluation toward target with obstacle avoidance and opponent-distance pressure
    cur_d_me = abs(tx - x) + abs(ty - y)
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp_next = abs(tx - ox) + abs(ty - oy)  # opponent assumed to move later; use current to keep deterministic
        # Prefer decreasing our distance; if tie, prefer increasing opponent distance advantage; then lexicographic dx,dy
        progress = cur_d_me - d_me
        mkey = (-progress, (d_me - d_opp_next), d_me, tx, ty, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # If all moves were blocked, stay
    return [best_move[0], best_move[1]]