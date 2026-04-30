def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_cells = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_cells.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    opp_pos = (ox, oy)
    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        next_pos = (nx, ny)

        # Advantage for capturing: larger means we reach that resource sooner than opponent.
        best_adv = -10**9
        best_our = 10**9
        best_target = None
        for r in resources:
            our_d = cheb(next_pos, r)
            opp_d = cheb(opp_pos, r)
            adv = opp_d - our_d
            if adv > best_adv or (adv == best_adv and our_d < best_our):
                best_adv, best_our, best_target = adv, our_d, r

        # Tie-break: prefer reducing distance to chosen target; also avoid moves that increase distance to any "hot" nearby resource.
        # "Hot" nearby = within 3 of current position.
        hot_bonus = 0
        for r in resources:
            if cheb((sx, sy), r) <= 3:
                if cheb(next_pos, r) < cheb((sx, sy), r):
                    hot_bonus += 1

        # Slight preference for moving toward the best target direction to prevent dithering.
        if best_target is not None:
            td_x = best_target[0] - nx
            td_y = best_target[1] - ny
            step_toward = 1 if (td_x == 0 or (td_x > 0) == (dx > 0) or dx == 0) and (td_y == 0 or (td_y > 0) == (dy > 0) or dy == 0) else 0
        else:
            step_toward = 0

        key = (best_adv, hot_bonus, step_toward, -best_our, -abs(nx - ox) - abs(ny - oy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]