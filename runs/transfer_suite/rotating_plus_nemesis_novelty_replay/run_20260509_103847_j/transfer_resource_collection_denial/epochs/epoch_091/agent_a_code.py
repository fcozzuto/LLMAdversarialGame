def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Determine our best resource and the opponent-nearest resource.
    my_best = None
    opp_best = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # positive means we are closer
        key_my = (-adv, ds, rx, ry)  # maximize adv, then nearer
        if my_best is None or key_my < my_best[0]:
            my_best = (key_my, (rx, ry), adv, ds, do)
        key_opp = (abs(rx - ox) + abs(ry - oy), rx, ry)  # opponent nearest
        if opp_best is None or key_opp < opp_best[0]:
            opp_best = (key_opp, (rx, ry), adv, ds, do)

    (tx, ty) = my_best[1]
    (px, py) = opp_best[1]
    # Intercept if it doesn't cost us too much and we can arrive no later.
    if opp_best[2] > -1 and (abs(px - sx) + abs(py - sy)) <= (abs(tx - sx) + abs(ty - sy)) + 1:
        # Aim at opponent resource unless it is essentially behind us in both axes.
        if (px - sx) * (tx - sx) >= 0 and (py - sy) * (ty - sy) >= 0:
            tx, ty = px, py

    # Choose move: prefer feasible, reduce our manhattan distance to target,
    # and slightly avoid moves that let opponent become closer to the target.
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_ours = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # If we would step onto a resource, strongly prefer.
        on_res = 1 if [nx, ny] in resources else 0
        # Local safety: avoid moving adjacent to obstacles only lightly (mostly pathing).
        wall_pen = 0
        for ax, ay in [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]:
            if inb(ax, ay) and (ax, ay) in obstacles:
                wall_pen += 1
        # Opponent-closer penalty for target.
        opp_closer = 1 if (d_opp - (abs(tx - (ox)) + abs(ty - (oy)))) > 0 else 0  # always 0, keep deterministic
        # Deterministic tie-break includes dx,dy ordering.
        score = (d_ours + wall_pen * 0.05 - on_res * 100 + opp_closer * 0.01, abs(dx) + abs(dy), dx, dy)
        if score < best_move:
            best_move = score

    return [best_move[2], best_move[3]]