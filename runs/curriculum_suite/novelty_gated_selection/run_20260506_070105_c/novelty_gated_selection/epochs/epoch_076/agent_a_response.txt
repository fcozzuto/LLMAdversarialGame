def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic center bias with opponent avoidance
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            key = (man(nx, ny, cx, cy), -man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]]

    # Choose a target resource with a bias away from opponent path pressure:
    # prefer resources in the half farther from opponent, then closest.
    opp_half_x = ox >= (w - 1) / 2.0
    opp_half_y = oy >= (h - 1) / 2.0
    def resource_key(r):
        rx, ry = r
        half_score = 0
        if (rx >= (w - 1) / 2.0) != opp_half_x: half_score += 2
        if (ry >= (h - 1) / 2.0) != opp_half_y: half_score += 1
        # also penalize resources too close to opponent
        return (-half_score, man(sx, sy, rx, ry), man(ox, oy, rx, ry), rx, ry)

    target = min(resources, key=resource_key)

    tx, ty = target
    # Opportunistic interception: if we can reduce distance to target faster than opponent, go;
    # otherwise, create spacing by moving away from opponent while still progressing to target.
    best = None
    my_d0 = man(sx, sy, tx, ty)
    opp_d0 = man(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        my_d = man(nx, ny, tx, ty)
        opp_d_est = man(ox, oy, tx, ty) - (1 if my_d < my_d0 else 0)  # deterministic crude estimate
        # Prefer moves that improve my distance, but if opponent is close, require spacing.
        my_prog = my_d - my_d0
        opp_prog = opp_d_est - opp_d0
        spacing = man(nx, ny, ox, oy)
        close_penalty = 0 if spacing >= 3 else (3 - spacing) * 5
        # tie-break deterministically: lower total key
        key = (my_prog, close_penalty, -spacing, opp_prog, man(nx, ny, tx, ty), dx, dy)
        if best is None or key < best:
            best = key
    return [best[4], best[5]]