def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obs_list)

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in role) or ("purs" in opp_role and "evad" not in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x, y):
        dx = x - ox; dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_val = None
    # Priority weights: capture dominates, then distance, then mobility, then safety from immediate threat
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        if nx == ox and ny == oy:
            val = 10**9 if pursuer else -10**9
        else:
            dist = d2(nx, ny)
            mob = mobility(nx, ny)

            # Approx threat: how close opponent could get next step if it moves like a pursuer
            # (still deterministic; doesn't assume exact opponent policy)
            min_opp_next = None
            for odx, ody in moves:
                tx, ty = ox + odx, oy + ody
                if inside(tx, ty) and (tx, ty) not in obs:
                    # If opponent can land on us next step, avoid hard
                    if tx == nx and ty == ny:
                        min_opp_next = 0
                        break
                    v = d2(nx, ny) if (tx, ty) == (ox, oy) else d2(tx, ty)  # keep deterministic calc
                    if min_opp_next is None or v < min_opp_next:
                        min_opp_next = v
            if min_opp_next is None:
                min_opp_next = dist

            if pursuer:
                val = (-dist) + 0.25 * mob + 0.001 * (min_opp_next)
            else:
                val = (dist) + 0.25 * mob - 0.001 * (min_opp_next)

        if best_val is None or (val > best_val) if not pursuer else (val > best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]