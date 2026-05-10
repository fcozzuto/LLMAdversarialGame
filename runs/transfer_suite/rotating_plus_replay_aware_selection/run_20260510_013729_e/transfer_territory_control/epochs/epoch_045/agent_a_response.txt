def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])

    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    un_list = list(unclaimed)
    oppt = (xo, yo)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # Precompute nearest-unclaimed heuristic for candidates
    def nearest_unclaimed_dist(nx, ny):
        if not un_list:
            return 999
        md = 999
        for (ux, uy) in un_list:
            d = abs(nx - ux) + abs(ny - uy)
            if d < md:
                md = d
                if md == 0:
                    break
        return md

    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
    cand_idx = 0
    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 60.0
        if (nx, ny) in myt:
            score += 14.0
        if (nx, ny) in opt:
            score -= 45.0  # entering opponent territory to flip is high-risk if contested

        d_un = nearest_unclaimed_dist(nx, ny)
        score += -1.8 * d_un

        d_opp = abs(nx - oppt[0]) + abs(ny - oppt[1])
        score += 0.35 * d_opp  # keep distance from opponent sweeper pressure

        score += -0.06 * (abs(nx - centerx) + abs(ny - centery))

        tie = (-(dx == 0 and dy == 0),)  # slight preference for moving
        key = (-score, tie, cand_idx)  # deterministic
        if best is None or key < best[0]:
            best = (key, [dx, dy])
        cand_idx += 1

    return best[1] if best is not None else [0, 0]