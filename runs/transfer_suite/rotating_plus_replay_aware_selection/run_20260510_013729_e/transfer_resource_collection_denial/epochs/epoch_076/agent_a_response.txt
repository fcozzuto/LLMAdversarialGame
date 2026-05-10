def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def pick_target(px, py):
        tr = observation.get("turns_remaining", 0)
        tight = 0.35 if tr <= 5 else 0.0
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # If we can arrive earlier, prioritize that; otherwise minimize our distance and maximize opponent distance.
            adv = od - sd
            key = (adv, -sd * (1.0 - tight) + od * tight, -sd)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, sd, od)
        return best

    tx, ty, sd, od = pick_target(sx, sy)

    # If we are clearly losing the target race, bias toward a different resource where we can do better.
    if od <= sd:
        t2 = pick_target(sx, sy)
        tx, ty, sd, od = t2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        # Evaluate relative race and also encourage reducing our distance.
        score = (nod - nsd) * 1000 - nsd
        # Deterministic tie-break: lexicographically smallest move after score tie.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]