def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Pick a resource that we can reach sooner than the opponent.
    # Score: our_dist weighted vs opponent_dist; tie-break deterministically.
    best_r = None
    best_sc = None
    for r in resources:
        d_me = man(me, r)
        d_opp = man(opp, r)
        sc = 2 * d_me - d_opp
        tb = (r[0], r[1])
        if best_sc is None or (sc, tb) < best_sc:
            best_sc = (sc, tb)
            best_r = r

    tx, ty = best_r
    # If opponent is overwhelmingly closer, switch to best "safer" resource.
    d_me = man(me, best_r)
    d_opp = man(opp, best_r)
    if d_opp + 2 < d_me:
        best_r = None
        best_sc = None
        for r in resources:
            d_me2 = man(me, r)
            d_opp2 = man(opp, r)
            # prefer resources that are not too late for us and also relatively far from opp
            sc = 3 * d_me2 - d_opp2
            tb = (r[0], r[1])
            # but strongly discourage ones the opponent can take immediately
            if d_opp2 + 1 < d_me2:
                sc += 50
            if best_sc is None or (sc, tb) < best_sc:
                best_sc = (sc, tb)
                best_r = r
        tx, ty = best_r

    # Choose move that minimizes distance to chosen target; slight tie-break to move away from opponent.
    chosen = None
    chosen_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            nx, ny = sx, sy  # engine keeps us; still deterministic
        d_to = abs(nx - tx) + abs(ny - ty)
        d_away = man((nx, ny), opp)
        val = (d_to, -d_away, nx, ny)
        if chosen_val is None or val < chosen_val:
            chosen_val = val
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]