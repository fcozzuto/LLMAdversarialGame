def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    step_to_opp = (0 if ox == sx else (1 if ox > sx else -1), 0 if oy == sy else (1 if oy > sy else -1))
    curd = man(sx, sy, ox, oy)

    def obs_clear(nx, ny):
        if not obs_set:
            return 99
        return min(abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs_set)

    best = None
    best_score = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        nd = man(nx, ny, ox, oy)

        hd_dx, hd_dy = step_to_opp
        align = dx * hd_dx + dy * hd_dy  # higher means moving toward opponent direction
        clear = obs_clear(nx, ny)

        # Deterministic score shaping; lower is better for pursuer, higher is better for evader
        if role == "pursuer":
            score = (
                nd,
                -align,
                -clear,
                abs(nx - ox) + abs(ny - oy),  # redundant but stabilizes
                0 if (dx, dy) == (0, 0) else 1,  # prefer moving when tied
            )
        else:
            # Evader: maximize distance, also prefer alignment away from opponent direction
            score = (
                -nd,
                align,     # move that aligns with step-to-opp is bad
                -clear,
                0 if (dx, dy) == (0, 0) else 1,
            )

        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]