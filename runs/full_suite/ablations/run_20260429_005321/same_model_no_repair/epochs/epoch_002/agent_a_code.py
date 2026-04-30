def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = list(observation.get("resources", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man2(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    def man(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # If no resources, just hold best move that keeps distance and avoids obstacles
    if not resources:
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            self_d = man2((nx, ny), (sx, sy))
            opp_d = man2((nx, ny), (ox, oy))
            score = (opp_d, -self_d, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose target resource: maximize (opponent can't beat us) + closeness priority
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = man((sx, sy), (rx, ry))
        od = man((ox, oy), (rx, ry))
        margin = od - sd  # positive means we are closer (likely)
        # tie-break: prefer farther margins and nearer to self; also deterministic ordering by coords
        key = (margin, -sd, -((rx << 4) + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Decide move: reduce distance to target; keep/extend advantage vs opponent; avoid obstacles and borders
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        ds_new = man((nx, ny), (tx, ty))
        do_new = man((nx, ny), (ox, oy))
        sd_now = man((sx, sy), (tx, ty))
        do_now = man((sx, sy), (ox, oy))

        adv_new = do_new - ds_new  # higher means opponent farther from target relative to us
        adv_now = do_now - sd_now

        # Also discourage stepping into immediate opponent pursuit (small deterministic bias)
        step_toward_opp = abs(nx - ox) + abs(ny - oy) < abs(sx - ox) + abs(sy - oy)

        # Prefer moves that either improve advantage or at least reduce self distance
        key = (
            adv_new - adv_now,       # immediate improvement
            adv_new,                 # overall advantage proxy
            -ds_new,                 # closer to target
            -do_new,                 # also keep opponent farther in absolute terms
            1 if (nx, ny) == (sx, sy) else 0,  # prefer moving over staying
            -(dx*dx + dy*dy),       # slight preference for smaller steps when otherwise equal
            (dx, dy)
        )

        # If stepping closer to opponent, penalize deterministically unless it greatly improves ds_new
        if step_toward_opp and ds_new >= sd_now:
            key = (key[0]-2, key[1]-2, key[2], key[3], key[4], key[5], key[6])

        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]