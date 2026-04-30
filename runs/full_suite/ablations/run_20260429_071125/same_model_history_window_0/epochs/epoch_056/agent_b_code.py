def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**9)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -(abs(tx - nx) + abs(ty - ny)) - 0.1 * (abs(ox - nx) + abs(oy - ny))
            if sc > best[1]:
                best = ((dx, dy), sc)
        return [best[0][0], best[0][1]]

    # Precompute top candidate resources by how close we are
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Consider a small deterministic subset for speed/brevity
    res_scored = []
    for r in resources:
        rx, ry = r[0], r[1]
        dme = man(sx, sy, rx, ry)
        # Prefer closer and relatively farther for opponent
        dop = man(ox, oy, rx, ry)
        res_scored.append((dme - dop, dme, rx, ry))
    res_scored.sort()
    candidates = res_scored[:6]

    # If opponent is close to a resource, bias toward taking a different one
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Bonus for grabbing a resource immediately if present at new pos
        grab_bonus = 0
        for _, _, rx, ry in candidates:
            if nx == rx and ny == ry:
                grab_bonus = 200
                break

        best_adv = -10**9
        # Compute our advantage against top resources from candidate position
        for _, _, rx, ry in candidates:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Lower myd and higher opd is better; also mildly prefer moving toward our currently best targets
            adv = (opd - myd) - 0.02 * myd + 0.01 * opd
            best_adv = adv if adv > best_adv else best_adv

        # Tactical defense: if we are close to opponent, keep distance unless it costs too much advantage
        dist_opp = man(nx, ny, ox, oy)
        defend = 0.15 * dist_opp

        sc = best_adv + grab_bonus + defend
        if sc > best[1]:
            best = ((dx, dy), sc)

    return [best[0][0], best[0][1]]