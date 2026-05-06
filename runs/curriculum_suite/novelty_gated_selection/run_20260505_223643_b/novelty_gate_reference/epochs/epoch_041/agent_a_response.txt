def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    # If no resources are visible, drift to center while keeping safe.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            d = man(nx, ny, tx, ty)
            key = (d, man(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]] if best else [0, 0]

    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Choose a resource to target maximizing advantage over opponent, then apply safety/anti-chase.
        # Deterministic tie-breaking by lexicographic resource cell.
        best_res = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Advantage: smaller self distance, larger opponent distance.
            # Slightly reward being near resource while also discouraging getting too close to opponent.
            adv = (od - sd) * 10 - sd
            key = (-adv, rx, ry)  # minimized key => max advantage; deterministic tie-break.
            if best_res is None or key < best_res[0]:
                best_res = (key, sd, od, rx, ry)
        if best_res is None:
            continue

        _, sd, od, rx, ry = best_res
        opp_next = man(nx, ny, ox, oy)
        # Safety: prefer keeping distance from opponent unless we have strong advantage.
        adv_strength = od - sd
        safety_pen = 0 if adv_strength >= 2 else (4 - min(4, opp_next)) * 3
        corner_pen = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)

        # Final key: prefer action with highest advantage to best resource, then shortest self distance, then safety.
        key = (-(od - sd), sd, safety_pen, corner_pen, man(nx, ny, rx, ry), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]