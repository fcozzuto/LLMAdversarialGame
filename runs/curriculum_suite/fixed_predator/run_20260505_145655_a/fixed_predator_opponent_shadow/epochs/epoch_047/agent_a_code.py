def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def blocked(nx, ny):
        return (nx, ny) in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    best = None
    best_tv = None
    for tx, ty in resources:
        d_me = man(x, y, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        lead = d_opp - d_me
        tv = lead * 1000 - d_me
        key = (-(abs(lead)), d_opp, tx, ty)  # deterministic tie-break
        tv2 = (tv, key)
        if best_tv is None or tv2 > best_tv:
            best_tv = tv2
            best = (tx, ty)

    tx, ty = best

    lead_now = man(ox, oy, tx, ty) - man(x, y, tx, ty)
    best_move = [0, 0]
    best_mscore = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d_after = man(nx, ny, tx, ty)
        d_opp_after = man(nx, ny, ox, oy)
        # If we are not leading, also try to avoid the opponent.
        mscore = d_after * 2 + d_opp_after * (1 if lead_now <= 0 else 0) + (abs(nx - ox) + abs(ny - oy)) * (0 if lead_now > 0 else 0.1)
        mscore_key = (mscore, d_after, d_opp_after, dx, dy)
        if best_mscore is None or mscore_key < best_mscore:
            best_mscore = mscore_key
            best_move = [dx, dy]

    return best_move