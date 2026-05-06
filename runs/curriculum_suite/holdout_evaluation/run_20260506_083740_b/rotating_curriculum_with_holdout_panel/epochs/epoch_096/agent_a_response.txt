def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_id(x, y):
        return y * 100 + x  # deterministic tie-break

    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Choose move that maximizes our potential gain over the opponent, while still making progress.
        best_adv = -10**18
        best_self = 10**9
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer to that resource than opponent
            # Give extra weight to resources we can actually reach earlier (adv > 0),
            # but still keep pressure when not.
            val = adv * 20 - sd
            if val > best_adv or (val == best_adv and (sd < best_self or (sd == best_self and cell_id(rx, ry) < cell_id(best_rx, best_ry)))):
                best_adv = val
                best_self = sd
                best_rx, best_ry = rx, ry
        # Additional deterministic bias: prefer moves that head toward the chosen resource.
        tx, ty = best_rx, best_ry
        progress = man(nx, ny, tx, ty)
        score = best_adv - progress
        if score > best[1]:
            best = ([dx, dy], score)
        elif score == best[1]:
            # tie-break by lexicographic move preference: closer to (0,0) dx then dy, then smaller cell id target
            if (dx, dy) < (best[0][0], best[0][1]):
                best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]