def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            try:
                px, py = int(p[0]), int(p[1])
            except:
                continue
            if inb(px, py):
                obs.add((px, py))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            try:
                rx, ry = int(p[0]), int(p[1])
            except:
                continue
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    if not inb(sx, sy):
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Target resource we are most likely to race for (positive advantage).
    best_r = None
    best_adv = -10**18
    best_selfd = 10**18
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # higher means opponent farther than we are
        # small tie-break toward being closer and toward center
        center_bias = -0.01 * (abs(rx - cx) + abs(ry - cy))
        key_adv = adv + center_bias
        if key_adv > best_adv or (key_adv == best_adv and sd < best_selfd):
            best_adv, best_selfd, best_r = key_adv, sd, (rx, ry)

    if best_r is None:
        # No resources; drift toward opponent's side deterministically.
        tx, ty = (ox, oy)
    else:
        tx, ty = best_r

    cur_sd = man(sx, sy, tx, ty)
    cur_od = man(ox, oy, tx, ty)

    # Choose move maximizing (reduce distance to target) and (prefer positions that worsen opponent's race).
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)  # opponent stationary this turn; include for consistency
        step_improve = cur_sd - nsd
        opp_race_worsen = (cur_od - nod)  # usually 0; kept for structural clarity
        center = -0.001 * (abs(nx - cx) + abs(ny - cy))
        # If tie, prefer staying on same row/col to reduce oscillation.
        axis_pref = -0.0005 * (0 if (dx == 0 or dy == 0) else 1)
        score = step_improve * 10 + opp_race_worsen + center + axis_pref
        if score > best_score or (score == best_score and (nsd < best_selfd or best_move == [0, 0])):
            best_score = score
            best_move = [dx, dy]

    return best_move