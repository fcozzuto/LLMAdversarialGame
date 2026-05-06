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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        dx = sign(ox - x)
        dy = sign(oy - y)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, -min_me_d, tie, dx, dy)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
        me_dists = []
        for tx, ty in resources:
            me_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            lead = opp_d - me_d
            # Prefer positions that let us be closer than opponent; otherwise still chase nearer resources.
            score = lead * 1000 - me_d
            me_dists.append((score, me_d))
        score, min_me_d = max(me_dists, key=lambda t: t[0])
        # Secondary preference: smaller distance to the selected best resource; deterministic tie.
        tie = (man(nx, ny, ox, oy), man(nx, ny, x, y))
        cand = (score, -min_me_d, tie, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[3]), int(best[4])]