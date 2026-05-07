def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    obstacles = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    if not res:
        return [0, 0]

    if (sx, sy) in set(res):
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    opp = (ox, oy)
    my = (sx, sy)
    best_delta = (0, 0)
    best_score = None

    # Prefer moves that secure a resource we can reach no later than opponent.
    # If none, contest the closest "most beatable" resource; otherwise reduce our distance.
    opp_to = [(r, man(opp, r)) for r in res]
    for dx, dy in legal:
        p = (sx + dx, sy + dy)
        dm_list = []
        for r, do in opp_to:
            dm = man(p, r)
            dm_list.append((r, dm, do))
        beatable = [x for x in dm_list if x[1] <= x[2]]
        if beatable:
            # maximize safety margin: (do - dm), then minimize dm, deterministic tie-break by coord
            r, dm, do = min(beatable, key=lambda t: (-(t[2] - t[1]), t[1], t[0][0], t[0][1]))
            score = (0, -((do - dm)), dm, r[0], r[1])
        else:
            # contest: smallest (dm - do), then minimize dm
            r, dm, do = min(dm_list, key=lambda t: (t[1] - t[2], t[1], t[0][0], t[0][1]))
            score = (1, (dm - do), dm, r[0], r[1])
        if best_score is None or score < best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]