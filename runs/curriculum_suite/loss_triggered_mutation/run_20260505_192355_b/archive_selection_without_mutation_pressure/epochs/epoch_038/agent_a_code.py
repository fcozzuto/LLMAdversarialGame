def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    best = None
    best_val = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        val = od - sd
        if val > best_val or (val == best_val and sd < (best[0] if best else 10**9)):
            best_val = val
            best = (sd, rx, ry)

    _, tx, ty = best if best else (man(sx, sy, int(resources[0][0]), int(resources[0][1])), int(resources[0][0]), int(resources[0][1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = man(nx, ny, tx, ty)
        cur_sd = man(sx, sy, tx, ty)
        sd_gain = cur_sd - sd
        od_now = man(ox, oy, tx, ty)
        od_after = od_now if not (inb(ox + 0, oy + 0)) else od_now
        score = sd_gain * 10 + (od_after - sd)
        if score > best_score or (score == best_score and (dx, dy) != (0, 0) and abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move