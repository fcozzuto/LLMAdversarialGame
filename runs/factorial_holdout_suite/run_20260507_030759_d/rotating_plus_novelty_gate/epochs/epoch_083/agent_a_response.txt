def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    res = [tuple(p) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]

    if not res:
        return [0, 0]
    if (sx, sy) in obs:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in set(res):
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))

    best_move = (0, 0)
    best_score = None

    opp = (ox, oy)
    my = (sx, sy)

    # Evaluate each candidate move by the best achievable "race advantage" over all resources.
    for dx, dy in legal:
        my2 = (sx + dx, sy + dy)
        # If we land on a resource, take it.
        if my2 in res:
            return [dx, dy]

        best_r = None
        best_r_adv = None
        best_r_selfd = None

        for r in res:
            selfd = md(my2, r)
            oppd = md(opp, r)
            adv = oppd - selfd  # positive means we are closer than opponent
            # Prefer larger advantage; then prefer smaller self distance to finish sooner.
            if best_r_adv is None or adv > best_r_adv or (adv == best_r_adv and selfd < best_r_selfd) or (
                adv == best_r_adv and selfd == best_r_selfd and r < best_r
            ):
                best_r_adv = adv
                best_r_selfd = selfd
                best_r = r

        # Penalize being far when no advantage exists; reward advantage strongly.
        score = (best_r_adv * 1000) - best_r_selfd
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]