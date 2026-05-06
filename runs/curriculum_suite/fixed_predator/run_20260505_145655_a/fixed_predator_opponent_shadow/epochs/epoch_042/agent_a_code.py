def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def target_value(tx, ty):
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    best_t = resources[0]
    best_tv = target_value(best_t[0], best_t[1])
    # Deterministic tie-break: smaller lead magnitude, then smaller d_opp, then lexicographic
    for r in resources[1:]:
        tx, ty = r[0], r[1]
        tv = target_value(tx, ty)
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        bt, by = best_t[0], best_t[1]
        bd_me = abs(bt - x) + abs(by - y)
        bd_opp = abs(bt - ox) + abs(by - oy)
        better = (tv > best_tv) or (tv == best_tv and (d_opp > bd_opp or (d_opp == bd_opp and (tx < bt or (tx == bt and ty < by)))))
        if better:
            best_t, best_tv = r, tv

    tx, ty = best_t[0], best_t[1]

    # Choose best immediate move via deterministic scoring; penalize stepping into obstacles/out-of-bounds.
    best_move = [0, 0]
    best_ms = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            ms = -10**12 + (dx == 0 and dy == 0)  # discourage; still allow stay if surrounded
        else:
            # primary: reduce distance to target more than opponent decreases theirs
            d_me_now = man((x, y), (tx, ty))
            d_opp_now = man((ox, oy), (tx, ty))
            d_me_next = man((nx, ny), (tx, ty))
            d_opp_next = d_opp_now  # opponent move unknown; keep invariant
            lead_next = d_opp_next - d_me_next
            ms = lead_next * 1000 - d_me_next
            # secondary: slight bias toward center-of-board for avoiding local traps
            ms += 0.001 * (4.0 - abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0))
        if ms > best_ms:
            best_ms = ms
            best_move = [dx, dy]

    # If target is current cell, keep position; otherwise move toward it (move selection above should handle it).
    if x == tx and y == ty:
        return [0, 0]
    return best_move