def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    myd0 = man(sx, sy, ox, oy)

    best_move = [0, 0]
    best_score = -10**18

    # Precompute resource list as tuples for speed/determinism
    res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res:
        return [0, 0]

    # Deterministic tie-break preference: center-ish, then staying still slightly disfavored
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Race score: prefer moves that most increase our "lead" to some resource.
        # Also penalize allowing opponent to get close to that resource.
        s = -0.12 * man(nx, ny, ox, oy)  # avoid being too easy to contest near us
        best_race = -10**18
        for rx, ry in res:
            my_d = man(nx, ny, rx, ry)
            op_d = man(ox, oy, rx, ry)
            lead = op_d - my_d
            # Capturing immediately is extremely valuable
            if my_d == 0:
                race = 10**6 + 0.5 * lead
            else:
                # Also encourage taking resources that are still good against opponent's baseline
                race = 3.0 * lead - 0.08 * op_d - 0.02 * my_d
            if race > best_race:
                best_race = race

            # Row-sweep pressure: if opponent can sweep to this resource along its row/col quickly,
            # we gain by moving to reduce our distance to same target row.
            # (Keeps behavior distinct from simple "nearest resource" only.)
            if ry == oy or rx == ox:
                rowcol_bias = -0.03 * min(abs(ny - ry), abs(nx - rx))
                s += rowcol_bias

        # Small center bias to reduce dithering
        cdx = nx - cx0
        cdy = ny - cy0
        center = -0.01 * (cdx * cdx + cdy * cdy)

        # If we move adjacent to opponent, slightly prefer it only when it improves race score strongly
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        adj_pen = -0.25 if adj else 0.0

        # Staying still discouraged unless it's best for racing
        stay_pen = -0.08 if (dx == 0 and dy == 0) else 0.0

        score = s + best_race + center + adj_pen + stay_pen

        # Robust deterministic tie-breaking
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # prefer non-stay, then lexicographic dx,dy
            if (dx, dy) != (0, 0) and best_move == [0, 0]:
                best_move = [dx, dy]
            elif (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]