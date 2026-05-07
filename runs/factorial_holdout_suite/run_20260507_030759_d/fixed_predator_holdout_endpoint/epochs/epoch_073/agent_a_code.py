def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d1(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    # Deterministic tie-break: fixed order in moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate by considering the best resource we could secure next while denying opponent.
        # If we are not closer, we still try to reduce opponent's advantage and steer toward resources in groups.
        best_val_for_move = -10**9
        for rx, ry in res:
            ds = d1(nx, ny, rx, ry)
            do = d1(ox, oy, rx, ry)
            # Secure if we can be at most tied; deny by maximizing (do - ds)
            # Add small bias to reduce ds to actually reach.
            adv = do - ds
            # If opponent is much closer, strongly discourage that target unless it helps overall deny.
            if adv < 0:
                val = 2 * adv - 0.7 * ds
            else:
                # Encourage tie-to-win: higher adv more important than raw distance
                val = 3 * adv - 0.2 * ds
            # Gentle preference for targets not behind heavy obstacles (local check: block straight line not searched; cheap proxy)
            # If target cell is adjacent-blocked, slightly reduce.
            blocked_adj = 0
            for tx in (-1, 0, 1):
                for ty in (-1, 0, 1):
                    ax, ay = rx + tx, ry + ty
                    if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                        blocked_adj += 1
            val -= 0.02 * blocked_adj
            if val > best_val_for_move:
                best_val_for_move = val

        # Additional deterrent: avoid moves that increase our distance to the most "reachable" resource set
        # (reachable = where we can beat opponent right now or near tie)
        # Cheap estimate: compute current max adv and next-step distance to best target.
        best_current = -10**9
        best_ds = 10**9
        for rx, ry in res:
            adv0 = d1(ox, oy, rx, ry) - d1(sx, sy, rx, ry)
            if adv0 > best_current:
                best_current = adv0
            ds0 = d1(nx, ny, rx, ry)
            if ds0 < best_ds:
                best_ds = ds0
        score = best_val_for_move + 0.05 * best_current - 0.01 * best_ds

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move