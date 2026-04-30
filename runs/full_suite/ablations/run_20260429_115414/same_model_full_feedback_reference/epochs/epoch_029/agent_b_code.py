def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    res_list = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res_list.append((x, y))

    if not res_list:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        if not inb(tx, ty):
            tx, ty = 0, 0
    else:
        def man(ax, ay, bx, by):
            dx = ax - bx
            if dx < 0: dx = -dx
            dy = ay - by
            if dy < 0: dy = -dy
            return dx + dy

        best = res_list[0]
        best_score = None
        for rx, ry in res_list:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Positive means we're closer. Tie-break by closeness.
            score = (do - ds) * 100 - ds
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man2(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    opp_dist_now = man2(ox, oy, tx, ty)
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds = man2(nx, ny, tx, ty)
        do = opp_dist_now
        # If we land on a resource, prioritize strongly.
        on_res = 1 if (nx, ny) in set(res_list) else 0
        # Score: minimize our distance, maximize our lead, avoid giving opponent lead.
        val = on_res * 100000 - ds * 20 + (do - ds) * 30
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]