def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obstacles:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (0, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (dx, dy) in legal:
            return [dx, dy]
        for a, b in legal:
            return [a, b]
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    best_cell = None
    best_val = None
    for rx, ry in res_set:
        d_self = abs(rx - sx) + abs(ry - sy)
        d_opp = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we can reach before opponent; penalize being too far and being too close to opponent
        close_pen = 0
        man_opp_me = abs(ox - sx) + abs(oy - sy)
        if man_opp_me <= 2:
            close_pen = (3 - man_opp_me) * 2
        val = (d_opp - d_self) * 10 - d_self - close_pen
        if best_val is None or val > best_val or (val == best_val and (rx + ry) < (best_cell[0] + best_cell[1])):
            best_val = val
            best_cell = (rx, ry)

    tx, ty = best_cell
    # Choose step that most reduces our distance to target; if tie, pick safer (farther from opponent)
    best_step = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nd_self = abs(tx - nx) + abs(ty - ny)
        nd_opp = abs(tx - ox) + abs(ty - oy)
        # Opponent proximity to our resulting cell
        opp_me = abs(ox - nx) + abs(oy - ny)
        step_score = (-nd_self * 3) + (nd_opp * 0) + (opp_me * 0.5)
        if best_score is None or step_score > best_score:
            best_score = step_score
            best_step = (dx, dy)
        elif step_score == best_score:
            # deterministic tiebreak: smaller dx magnitude, then smaller dy magnitude
            if abs(dx) < abs(best_step[0]) or (abs(dx) == abs(best_step[0]) and abs(dy) < abs(best_step[1])):
                best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]