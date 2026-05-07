def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not res:
        return [0, 0]

    if (sx, sy) in set(res):
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    my = (sx, sy)
    opp = (ox, oy)

    best_move = None
    best_key = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my2 = (nx, ny)

        # Resource worth taking soon, while preferring denial of resources opponent is closer to.
        # Key = (maximize advantage, then minimize own distance to a good target, then deterministic tiebreak)
        best_adv = None
        best_d = None
        best_r = None
        for r in res:
            my_d = md(my2, r)
            op_d = md(opp, r)
            adv = op_d - my_d  # positive means we are closer after the move
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_d is None or my_d < best_d)) or (adv == best_adv and my_d == best_d and (best_r is None or r < best_r)):
                best_adv, best_d, best_r = adv, my_d, r

        # Secondary: if we can land on any resource, prioritize it decisively.
        land = 1 if (nx, ny) in set(res) else 0
        key = (land, best_adv if best_adv is not None else -10**9, -best_d if best_d is not None else -10**9, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]