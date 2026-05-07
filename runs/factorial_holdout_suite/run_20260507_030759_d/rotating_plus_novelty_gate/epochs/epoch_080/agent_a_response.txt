def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obstacles_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles_set.add((p[0], p[1]))
    res_list = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res_list.append((p[0], p[1]))
    res_set = set(res_list)

    if (sx, sy) in res_set:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles_set:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not res_list:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    mypos = (sx, sy)
    opppos = (ox, oy)

    # Choose target resource we are (or can quickly become) closer to than the opponent.
    best_r = None
    best_adv = None
    for r in res_list:
        dm = md(mypos, r)
        do = md(opppos, r)
        adv = do - dm  # positive => we are closer
        # tie-break: higher adv, then smaller our distance, then lexicographic
        key = (adv, -dm, -r[0], -r[1])
        if best_r is None or key > (best_adv, -md(mypos, best_r), -best_r[0], -best_r[1]):
            best_r = r
            best_adv = adv

    # If we can't beat them on the target, pick a resource that is "least losing" and step toward it.
    if best_r is None:
        best_r = sorted(res_list)[0]

    # Evaluate each possible move by resulting advantage on best target, with a small component for overall advantage.
    target = best_r
    best_move = None
    best_score = None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        # If stepping onto a resource is possible, prioritize it deterministically.
        if (nx, ny) in res_set:
            return [dx, dy]
        dm_next = md((nx, ny), target)
        do = md(opppos, target)
        adv_next = do - dm_next

        # secondary: prefer making our position generally closer to the nearest remaining resource than the opponent.
        sec_best = -10**9
        for r in res_list:
            dmn = md((nx, ny), r)
            dor = md(opppos, r)
            sec_best = max(sec_best, dor - dmn)

        score = (adv_next, sec_best, -dm_next, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]