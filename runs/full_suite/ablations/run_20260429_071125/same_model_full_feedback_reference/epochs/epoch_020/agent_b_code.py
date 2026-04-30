def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    # Materially different from simple "race to nearest": evaluate move by best denied/secured resource.
    # Prefer resources where we are closer than opponent, otherwise deny the opponent's closest targets.
    best_move = (0, 0)
    best_score = -10**9
    center_bias = ((w - 1) - sx) * 0.01 + ((h - 1) - sy) * 0.01  # keep drifting toward our corner

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        self_to_opp = man(nx, ny, ox, oy)
        # Avoid walking into opponent when it doesn't improve resource securing.
        opp_pen = 0.0
        if self_to_opp <= 1:
            opp_pen = -0.8

        local_best = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we can secure it sooner, large positive. If we can't, try to deny (maximize opponent delay).
            diff = od - sd  # >0 means we're closer
            # Normalize by urgency (smaller sd/od are better), deterministic tie-break by closer to our corner.
            urgency = 0.0
            if diff >= 0:
                urgency = 2.5 * (1.0 / (1 + sd)) + 1.2 * (1.0 / (1 + od))
            else:
                urgency = 1.4 * (1.0 / (1 + od)) - 0.9 * (1.0 / (1 + sd))
            corner_tb = ((w - 1 - rx) + (h - 1 - ry)) * 0.002
            val = diff + urgency + corner_tb
            if val > local_best:
                local_best = val

        score = local_best + opp_pen + center_bias
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]