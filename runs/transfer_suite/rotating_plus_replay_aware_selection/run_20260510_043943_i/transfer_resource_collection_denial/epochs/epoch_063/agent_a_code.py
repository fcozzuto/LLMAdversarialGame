def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    # evaluate each immediate move by the best resource we could reach first for
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            if nx == sx and ny == sy and (dx, dy) != (0, 0):
                continue

        chosen_adv = -10**9
        chosen_dist = 10**9
        chosen_opp_dist = 10**9

        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # prefer resources where we are earlier; tie-break by shorter self distance,
            # then by longer opponent distance, then by resource ordering stability.
            adv = (od - sd)
            if adv > chosen_adv or (adv == chosen_adv and (sd < chosen_dist or (sd == chosen_dist and od > chosen_opp_dist))):
                chosen_adv, chosen_dist, chosen_opp_dist = adv, sd, od

        # overall move preference: maximize advantage, then minimize our distance, then maximize opponent distance
        move_score = (chosen_adv, -chosen_dist, chosen_opp_dist, -(nx + 13 * ny))
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]