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

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    def tv(tx, ty):
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    best = resources[0]
    best_score = tv(best[0], best[1])
    for r in resources[1:]:
        s = tv(r[0], r[1])
        if s > best_score:
            best_score = s
            best = r
        elif s == best_score:
            if (r[0], r[1]) < (best[0], best[1]):
                best = r

    tx, ty = best[0], best[1]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_mscore = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me2 = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead2 = d_opp - d_me2
        # Prefer taking/maintaining lead; slight bias toward reducing distance and staying safe from obstacles
        safe = 0
        if any(in_bounds(nx + adx, ny + ady) and not blocked(nx + adx, ny + ady) for adx, ady in dirs):
            safe = 1
        mscore = lead2 * 1000 - d_me2 + 0.5 * safe - 0.001 * (abs(ox - nx) + abs(oy - ny))
        if mscore > best_mscore or (mscore == best_mscore and (dx, dy) < best_move):
            best_mscore = mscore
            best_move = (dx, dy)

    # If all candidate moves were blocked (unlikely), step deterministically toward target while staying in bounds
    if best_move == (0, 0) and blocked(x, y):
        dx = sign(tx - x)
        dy = sign(ty - y)
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and not blocked(nx, ny):
            return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]