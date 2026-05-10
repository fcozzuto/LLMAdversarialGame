def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    # Pick a target we can likely reach first; if none, pick the best "race" option.
    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        ds = man(rx, ry, sx, sy)
        do = man(rx, ry, ox, oy)
        closer_bonus = do - ds  # positive means we are closer
        # Add a slight "advance toward opponent" bias to avoid oscillation
        adv = (1 if ox > sx else -1) * (rx - sx) + (1 if oy > sy else -1) * (ry - sy)
        sc = closer_bonus * 1000 - ds + adv * 0.01
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_msc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        # Prefer moves that decrease our distance to target; tie-break by increasing distance from opponent.
        d_new = man(nx, ny, tx, ty)
        d_old = man(sx, sy, tx, ty)
        opp_new = man(nx, ny, ox, oy)
        opp_old = man(sx, sy, ox, oy)
        step_sc = (d_old - d_new) * 10 + (opp_new - opp_old) * 0.1
        # If we are moving into a resource cell, strongly prefer it.
        if (nx, ny) in set(resources):
            step_sc += 10000
        if step_sc > best_msc:
            best_msc = step_sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]