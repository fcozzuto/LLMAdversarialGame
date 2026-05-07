def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Drift toward a safe central bias away from opponent corner
        tx = gw // 2
        ty = gh // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for cand in ([dx, dy], [dx, 0], [0, dy], [0, 0]):
            nx, ny = sx + cand[0], sy + cand[1]
            if legal(nx, ny):
                return [cand[0], cand[1]]

    # Score moves by best advantage over a chosen resource after the move.
    best = None  # (score, selfdist, oppdist, nx, ny, rx, ry)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer resources where we are closer than opponent; also prefer reducing our distance fast.
        best_here = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Immediate grab preference
            if sd == 0:
                adv = 10**6
            else:
                # Advantage: lower our distance, higher opponent distance.
                # Contested resources (od <= sd) penalized strongly.
                contest_pen = 2000 if od <= sd else 0
                adv = (od - sd) * 120 - contest_pen - sd * 5

            # Small tie-break to avoid oscillation: favor progress compared to staying
            curr_sd = man(sx, sy, rx, ry)
            progress = curr_sd - sd  # positive if we move closer

            total = adv + progress * 25
            cand = (total, sd, od, rx, ry)
            if best_here is None or cand > best_here:
                best_here = cand

        if best_here is None:
            continue
        total, sd, od, rx, ry = best_here
        key = (total, -sd, -od, nx, ny, rx, ry)
        if best is None or key > best:
            best = key

    # Deterministically return the move corresponding to best key.
    total, _, _, bx, by, _, _ = best
    return [bx - sx, by - sy]