def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_score = -10**18
    best_move = (0, 0)

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # Pick the resource where we are relatively closest to capture first vs the opponent.
        chosen = None
        max_adv = -10**18
        chosen_sd = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # higher => we are closer than opponent
            if adv > max_adv or (adv == max_adv and (chosen is None or sd < chosen_sd)):
                max_adv = adv
                chosen = (rx, ry)
                chosen_sd = sd

        # Evaluation: maximize relative advantage, then minimize our distance to that chosen target.
        score = max_adv * 100 - (chosen_sd if chosen_sd is not None else 0)

        if score > best_score or (score == best_score and (dxm, dym) < best_move):
            best_score = score
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]