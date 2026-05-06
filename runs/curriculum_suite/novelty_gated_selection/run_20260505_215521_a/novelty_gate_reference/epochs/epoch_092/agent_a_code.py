def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def clamp(v, a, b):
        return a if v < a else b if v > b else v

    def eval_from(posx, posy):
        bx = ox - posx
        by = oy - posy
        self_opp_sep = abs(bx) + abs(by)

        best = -10**18
        for rx, ry in resources:
            sd = abs(rx - posx) + abs(ry - posy)
            od = abs(rx - ox) + abs(ry - oy)

            # advantage: prefer resources we can reach sooner
            adv = od - sd

            # anti-sweep: if resource is on/near opponent row and aligned, penalize
            same_row = 1 if ry == oy else 0
            near_row = 1 if abs(ry - oy) <= 1 else 0
            aligned = 1 if rx == ox else 0
            sweep_pen = 3 * same_row + 1 * near_row + 2 * aligned

            # progress bias: prefer closer targets when advantage is similar
            prog = -sd

            # also lightly prefer targets that are "not behind" opponent sweep direction (towards sy..)
            dir_bias = -clamp((ry - sy) * (oy - sy), -4, 4) * 0.25

            val = 2.2 * adv + prog + dir_bias - sweep_pen + 0.03 * self_opp_sep
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = eval_from(nx, ny)
        if v > best_val + 1e-9:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]