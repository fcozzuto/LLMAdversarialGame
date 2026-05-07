def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            px, py = int(p[0]), int(p[1])
            if inside(px, py):
                blocked.add((px, py))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    # Choose target with strongest advantage (we being closer)
    best_t = res[0]
    best_adv = -10**9
    for rx, ry in res:
        sd = man(rx, ry, sx, sy)
        od = man(rx, ry, ox, oy)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd, rx, ry) < (man(best_t[0], best_t[1], sx, sy), best_t[0], best_t[1])):
            best_adv = adv
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_val = -10**18
    best_move = [0, 0]

    # Prefer moving toward the chosen target, but only if it improves relative advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        sd = man(tx, ty, nx, ny)
        od = man(tx, ty, ox, oy)
        # Small tie-breaker: reduce distance to target and avoid lingering
        val = (od - sd) * 100 - sd - (0 if dx == 0 and dy == 0 else 0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move != [0, 0] else [0, 0]