def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Go to center while avoiding obstacles
        cx, cy = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        bd = None
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not free(nx, ny):
                continue
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if cand < best:
                best = cand
                bd = (dx, dy)
        return list(bd if bd is not None else (0, 0))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not free(nx, ny):
            continue

        # Evaluate best resource we can "win" by reaching earlier than opponent
        best_adv = -10**9
        best_myd = 10**9
        best_res = None
        for tx, ty in resources:
            myd = abs(nx - tx) + abs(ny - ty)
            opd = abs(ox - tx) + abs(oy - ty)
            adv = opd - myd  # higher means we reach earlier
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and (tx, ty) < (best_res or (10**9,10**9))))):
                best_adv = adv
                best_myd = myd
                best_res = (tx, ty)

        # Prefer strong advantage; if tied, prefer closer resource and safer from opponent
        oppd_near = abs(nx - ox) + abs(ny - oy)
        score = (best_adv, -best_myd, oppd_near, -abs((nx + ny) - (mx + my)), -dx*dx - dy*dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]