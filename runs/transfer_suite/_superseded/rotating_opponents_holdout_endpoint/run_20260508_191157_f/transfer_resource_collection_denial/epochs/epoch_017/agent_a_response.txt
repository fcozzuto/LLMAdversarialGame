def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation["grid_width"]
    h = observation["grid_height"]

    if not resources:
        # drift toward center to reduce worst-case corner trapping
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    obst = set((p[0], p[1]) for p in obstacles)

    def step_toward(x, y, t):
        tx, ty = t
        return (0 if tx == x else (1 if tx > x else -1), 0 if ty == y else (1 if ty > y else -1))

    def best_target_score(x, y):
        # maximize (opp_dist - self_dist), tie by smaller self_dist (faster collection)
        best = None
        for r in resources:
            rx, ry = r
            sd = abs(rx - x) + abs(ry - y)
            od = abs(rx - ox) + abs(ry - oy)
            sc = (od - sd, -sd)
            if best is None or sc > best[0]:
                best = (sc, (rx, ry))
        return best[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        sc = best_target_score(nx, ny)
        # small bias: move also closer to currently best target to avoid oscillation
        # (derived deterministically from sc components)
        value = sc[0] * 1000 + sc[1]
        # obstacle deterrence for next step: if direct next toward best target would hit obstacle, penalize
        if resources:
            # recompute best target deterministically
            best_sd = None
            best_r = resources[0]
            for r in resources:
                rx, ry = r
                sd = abs(rx - nx) + abs(ry - ny)
                od = abs(rx - ox) + abs(ry - oy)
                if best_sd is None or (od - sd, -sd) > best_sd:
                    best_sd = (od - sd, -sd)
                    best_r = r
            bx, by = best_r
            sdx, sdy = step_toward(nx, ny, (bx, by))
            nnx, nny = nx + sdx, ny + sdy
            if 0 <= nnx < w and 0 <= nny < h and (nnx, nny) in obst:
                value -= 50
        if value > best_move[1]:
            best_move = ((dx, dy), value)

    if best_move[0] is None:
        # fallback: greedy toward best resource by score
        best_r = resources[0]
        best_sc = None
        for r in resources:
            rx, ry = r
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            sc = (od - sd, -sd)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_r = r
        dx, dy = step_toward(sx, sy, best_r)
        return [dx, dy]

    return [best_move[0][0], best_move[0][1]]