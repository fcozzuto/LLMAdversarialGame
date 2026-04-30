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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # pick best contested resources (top 2 by advantage)
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # prefer resources where we are closer than opponent; small tie-break to be closer overall
        scored.append((od - sd, -sd, rx, ry))
    scored.sort(reverse=True)
    top = scored[:2] if len(scored) >= 2 else scored[:1]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0.0
        for adv, negsd, rx, ry in top:
            sd2 = man(nx, ny, rx, ry)
            od2 = man(ox, oy, rx, ry)
            # primary: keep advantage over opponent; secondary: reduce our distance
            val += (od2 - sd2) - 0.08 * sd2
        # tiny bias to avoid dithering: prefer moves that reduce our distance to best target
        if top:
            rx, ry = top[0][2], top[0][3]
            val += -0.01 * (man(nx, ny, rx, ry) - man(sx, sy, rx, ry))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]