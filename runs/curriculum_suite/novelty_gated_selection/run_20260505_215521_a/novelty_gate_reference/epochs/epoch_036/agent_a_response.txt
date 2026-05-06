def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_target_from(posx, posy):
        if not resources:
            return None
        best = None
        for x, y in resources:
            sd = abs(x - posx) + abs(y - posy)
            od = abs(x - ox) + abs(y - oy)
            edge_bias = min(x, y, w - 1 - x, h - 1 - y)  # prefer center vs edge_patrol
            edge_bonus = -edge_bias
            # Want resources closer to us, farther from opponent, and not too close to them
            val = (sd - 1.15 * od) + 0.08 * sd - 0.15 * edge_bonus
            if best is None or val < best[0]:
                best = (val, x, y, sd, od)
        return best

    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    cur = best_target_from(sx, sy)
    cur_x, cur_y = cur[1], cur[2]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        t = best_target_from(nx, ny)
        if t is None:
            continue
        val, tx, ty, sd, od = t
        # add a small preference to keep progressing toward current target
        prog = abs(cur_x - nx) + abs(cur_y - ny)
        val2 = val + 0.02 * prog
        if best_val is None or val2 < best_val:
            best_val = val2
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move