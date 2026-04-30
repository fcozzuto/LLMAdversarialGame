def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        tx = w - 1 if ox > sx else 0
        ty = h - 1 if oy > sy else 0
        best = (0, 0)
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            s = -dist((nx, ny), (tx, ty)) - 0.25 * dist((nx, ny), opp)
            if s > best_s:
                best_s = s
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a target resource I can reach earlier than the opponent.
    best_target = resources[0]
    best_key = None
    for r in resources:
        dme = dist(my, r)
        dpo = dist(opp, r)
        # Prefer resources where I am closer; tiebreak by larger gap, then nearer.
        key = (dpo - dme, -dme)
        if best_key is None or key > best_key:
            best_key = key
            best_target = r

    # Evaluate immediate move.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nm = (nx, ny)
        dme = dist(nm, best_target)
        dpo = dist(opp, best_target)
        # Push toward target, while gaining capture advantage; slight repulsion from opponent.
        capture_adv = (dpo - dme)
        score = 3.0 * capture_adv - 1.0 * dme - 0.15 * dist(nm, opp)
        # Opportunistic: if moving near any resource, add small bonus.
        near_res = 10**9
        for r in resources:
            d = dist(nm, r)
            if d < near_res:
                near_res = d
        score += 0.25 * (-near_res)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]