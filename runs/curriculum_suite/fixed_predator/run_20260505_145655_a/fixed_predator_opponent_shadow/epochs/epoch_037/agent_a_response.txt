def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        # deterministic: chase opponent (opponent_shadow can be active), but keep pressure
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    # Pick best resource: primarily maximize lead (opp farther than us), then minimize our distance,
    # then slightly prefer resources more "lateral" vs opponent to reduce head-on contests.
    best = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        lateral = abs(tx - x) - abs(ty - y)
        key = (lead, -d_me, -abs(lateral))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # Greedy one-step with deterministic obstacle-aware tie-breaking.
    # Evaluate successor states by how much they improve lead to the target.
    best_move = [0, 0]
    best_mv_key = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d_me2 = abs(tx - nx) + abs(ty - ny)
        d_opp2 = abs(tx - ox) + abs(ty - oy)
        lead2 = d_opp2 - d_me2
        # Also discourage moves that let opponent be closer to the same target than us.
        opp_close_pen = man((ox, oy), (nx, ny))
        key = (lead2, -d_me2, -opp_close_pen)
        if best_mv_key is None or key > best_mv_key:
            best_mv_key = key
            best_move = [dx, dy]

    # If all moves are blocked (unlikely), do nothing.
    return best_move if best_mv_key is not None else [0, 0]