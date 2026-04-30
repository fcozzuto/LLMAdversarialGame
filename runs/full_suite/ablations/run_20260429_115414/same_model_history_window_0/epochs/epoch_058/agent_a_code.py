def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    cand = []
    for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))

    if not cand:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Predict opponent next step: move toward its nearest resource (deterministically)
    opp_next = (ox, oy)
    if resources:
        best = None
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = ox + dx, oy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dmin = None
                for r in resources:
                    dd = dist2((nx, ny), r)
                    if dmin is None or dd < dmin:
                        dmin = dd
                if best is None or dmin < best[0]:
                    best = (dmin, nx, ny)
        if best:
            opp_next = (best[1], best[2])

    # Score each move: prefer resources where we are closer than opponent, while staying away from opponent
    best_move = None
    best_score = None
    for dx, dy, nx, ny in cand:
        if (nx, ny) == (ox, oy):
            score = -10**9
        else:
            opp_factor = -0.6 * dist2((nx, ny), opp_next)
            closest_me = None
            steal_bonus = 0.0
            for r in resources:
                dm = dist2((nx, ny), r)
                do = dist2(opp_next, r)
                if closest_me is None or dm < closest_me:
                    closest_me = dm
                if dm <= do:
                    # Being closer than (or tied with) opponent at a resource is valuable
                    steal_bonus += (do - dm) / 10.0
            # Also lightly discourage moving into immediate opponent proximity
            prox_pen = 0.0
            dmo = dist2((nx, ny), (ox, oy))
            if dmo <= 4:
                prox_pen = -3.0
            # Prefer fewer remaining steps to some resource
            score = (0 if closest_me is None else -closest_me) + steal_bonus + opp_factor + prox_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]