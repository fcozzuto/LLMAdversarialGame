def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    if not resources:
        # Deterministic drift to center to keep options open
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def md(x1, y1, x2, y2):
        return (x1 - x2 if x1 >= x2 else x2 - x1) + (y1 - y2 if y1 >= y2 else y2 - y1)

    best_key = None
    best_move = (0, 0)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose the resource where we have the best "will-reach-first" advantage
        best_adv = -10**9
        best_res = resources[0]
        for rx, ry in resources:
            our = md(nx, ny, rx, ry)
            opp = md(ox, oy, rx, ry)
            adv = opp - our  # positive if we are closer than opponent
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)

        rx, ry = best_res
        our_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)

        # Heuristic:
        # 1) maximize advantage (opp - our)
        # 2) if tied, prioritize closer to the target
        # 3) if still tied, avoid being too close to opponent (less likely to waste turns on contested route)
        # 4) deterministic tie-breaker by move order
        key = (-best_adv, our_d, abs(nx - ox) + abs(ny - oy), dx, dy, opp_d)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]