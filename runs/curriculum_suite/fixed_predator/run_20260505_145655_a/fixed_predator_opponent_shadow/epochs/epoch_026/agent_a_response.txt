def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Pick best target resource deterministically
    best_t = None
    best_tv = -10**18
    for tx, ty in resources:
        d_me = md(x, y, tx, ty)
        d_opp = md(ox, oy, tx, ty)
        lead = d_opp - d_me
        tv = lead * 1000 - d_me + d_opp * 0.01
        if tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cur_to_opp = md(x, y, ox, oy)
    cur_to_t = md(x, y, tx, ty)

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        new_to_t = md(nx, ny, tx, ty)
        new_to_opp = md(nx, ny, ox, oy)

        # Primary: move closer to the chosen lead resource
        # Secondary: avoid allowing opponent to get closer faster
        # Tertiary: prevent "oscillation" by preferring progress (smaller new_to_t)
        prog = (cur_to_t - new_to_t)  # positive is good
        lead_now = md(ox, oy, tx, ty) - new_to_t  # higher means we're closer relative to opponent
        opp_change = (new_to_opp - cur_to_opp)

        score = prog * 50 + lead_now * 1.0 - opp_change * 0.2
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        # All directions blocked (rare); fall back to deterministic direction to target
        return [-sign(tx - x), -sign(ty - y)]

    return [best[0][0], best[0][1]]