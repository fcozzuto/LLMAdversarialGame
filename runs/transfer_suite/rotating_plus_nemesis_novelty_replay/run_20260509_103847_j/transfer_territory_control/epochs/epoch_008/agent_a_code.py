def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    un_list = list(unT)
    if un_list:
        un_list.sort(key=lambda p: dist(sx, sy, p[0], p[1]))
        candidates = un_list[:10]
        best_cell, best_score = None, -10**9
        for tx, ty in candidates:
            # Prefer cells we can take and that are "safer" from opponent reach.
            score = 2 * dist(ox, oy, tx, ty) - dist(sx, sy, tx, ty)
            if (tx, ty) in selfT:
                score -= 1000
            if score > best_score:
                best_score = score
                best_cell = (tx, ty)
        target = best_cell
    else:
        # No unclaimed: head toward opponent territory to flip/contest.
        op_list = list(opT)[:]
        if not op_list:
            target = (w // 2, h // 2)
        else:
            op_list.sort(key=lambda p: dist(sx, sy, p[0], p[1]))
            target = op_list[0]

    tx, ty = target if target is not None else (w // 2, h // 2)

    our_count = int(observation.get("self_territory_count", len(selfT)))
    op_count = int(observation.get("opponent_territory_count", len(opT)))
    behind = our_count <= op_count

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        val = 0
        if (nx, ny) in unT:
            val += 80 if behind else 60
        if (nx, ny) in opT:
            val += 130 if behind else 110
        # Greedy toward target.
        val += 40 * (dist(sx, sy, tx, ty) - dist(nx, ny, tx, ty))
        # Slight bias to avoid aimless moves when target is reached.
        if (nx, ny) == (sx, sy) and (nx, ny) not in unT and (nx, ny) not in opT:
            val -= 15
        # If close to opponent territory, prioritize contact.
        if behind:
            d_op = min(dist(nx, ny, px, py) for (px, py) in (opT or [(ox, oy)]))
            val += 20 if d_op <= 2 else 0
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move