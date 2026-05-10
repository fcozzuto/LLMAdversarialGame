def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target selection: prefer resources we are clearly closer to; if none, contest nearest.
    best = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        diff = sd - od  # <=0 means we are closer or equal
        contest_pen = diff if diff > 0 else 0
        key = (contest_pen * 6 + sd, abs(tx - sx) + abs(ty - sy), -od, tx, ty)
        if best is None or key < best:
            best = key
            target = (tx, ty)

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Local move choice: head toward target, avoid obstacles and briefly avoid moving closer to opponent.
    best_m = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        d_opp_now = man(sx, sy, ox, oy)
        # If opponent is also very close to the target, slight preference to keep distance from opponent.
        if man(ox, oy, tx, ty) <= man(sx, sy, tx, ty):
            opp_term = d_opp_now - d_opp
        else:
            opp_term = 0
        key_m = (d_to_t, opp_term, man(nx, ny, sx, sy), nx, ny)
        if best_m is None or key_m < best_m:
            best_m = key_m
            best_move = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]