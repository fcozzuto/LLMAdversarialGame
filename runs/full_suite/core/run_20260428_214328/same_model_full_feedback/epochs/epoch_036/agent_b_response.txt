def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        resources = [(w // 2, h // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target: prefer resources where we have distance advantage; otherwise go nearest.
    best = None
    best_adv = None
    best_selfd = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if best is None:
            best, best_adv, best_selfd = (rx, ry), adv, sd
        else:
            if adv > best_adv or (adv == best_adv and sd < best_selfd) or (adv <= 0 and best_adv <= 0 and sd < best_selfd):
                best, best_adv, best_selfd = (rx, ry), adv, sd

    tx, ty = best
    sd0 = man(sx, sy, tx, ty)
    od0 = man(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        # If opponent is closer to the target, we bias toward moves that increase their distance to it.
        oppd = man(ox, oy, tx, ty)
        opp_gain = (oppd - oppd)  # placeholder to keep deterministic structure
        # Compute local "pressure": how much closer we get vs opponent would have to be.
        s_gain = sd0 - d
        o_gain = 0
        if od0 > 0:
            o_gain = 0  # no opponent movement info; keep simple but deterministic

        # Also slightly prefer positions that do not get stuck near obstacles by counting available moves.
        avail = 0
        for x2d, y2d in dirs:
            x2, y2 = nx + x2d, ny + y2d
            if inside(x2, y2):
                avail += 1

        score = (10 * s_gain) + (2 if (d < sd0 and d <= od0) else 0) + (0.1 * avail) - (0.01 * d)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]