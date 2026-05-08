def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If possible, pick a resource where we are currently advantaged.
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                da = md(sx, sy, x, y)
                db = md(ox, oy, x, y)
                res.append((x, y, da, db))

    advantaged = [t for t in res if t[2] + 0 < t[3] - 1]  # strictly better by at least 1
    target_list = advantaged if advantaged else res

    # Deterministically select the best target based on advantage, then closeness.
    best_t = None
    best_key = None
    for x, y, da, db in target_list:
        key = (-(db - da), da, md(ox, oy, w - 1 - x, h - 1 - y))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (x, y, da, db)
    if best_t is None:
        # fallback: move toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -(md(nx, ny, tx, ty)) + 0.05 * md(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best_move = [dx, dy]
        return best_move

    tx, ty, _, _ = best_t

    # Move evaluation: prioritize taking/approaching target; penalize moving into squares that worsen our advantage.
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_d = md(nx, ny, tx, ty)
        opp_d_to_same = md(ox, oy, tx, ty)
        my_adv_now = (opp_d_to_same - my_d)  # higher is better (we're closer than opponent)

        # Also consider whether this square makes us lose access to other resources.
        worst_loss = 10**9
        for x, y, da, db in res[:10]:  # deterministic cap; order as provided by observation
            dnew = md(nx, ny, x, y)
            loss = (dnew - db)  # positive means opponent likely closer
            if loss < worst_loss:
                worst_loss = loss

        v = 200 - 5 * my_d + 20 * my_adv_now - 2 * (worst_loss)  # tuned shaping
        if v > bestv:
            bestv = v
            best_move = [dx, dy]

    return best_move