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

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def best_adv(nx, ny):
        best = None
        for tx, ty in resources:
            d_me = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me
            val = lead * 1000 - d_me + 0.01 * d_opp
            if best is None or val > best[0] or (val == best[0] and (d_me < best[1] or (d_me == best[1] and (tx, ty) < best[2]))):
                best = (val, d_me, (tx, ty))
        return best[0]

    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # One-step lookahead with tie-break that prefers moves that move closer to currently "best" targets
        adv = best_adv(nx, ny)
        opp_close = abs(nx - ox) + abs(ny - oy)
        self_close = 0
        # approximate self_close via nearest resource
        sc = None
        for tx, ty in resources:
            d = abs(tx - nx) + abs(ty - ny)
            if sc is None or d < sc or (d == sc and (tx, ty) < best_t):
                sc = d
                best_t = (tx, ty)
        self_close = sc
        candidates.append((adv, -self_close, opp_close, dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]