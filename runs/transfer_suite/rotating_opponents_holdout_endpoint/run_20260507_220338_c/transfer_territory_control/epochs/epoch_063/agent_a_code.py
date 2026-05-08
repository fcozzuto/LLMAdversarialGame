def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles") or []
    blocks = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    res_list = observation.get("resources") or []
    targets = []
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocks:
                targets.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cur_res = md(sx, sy, targets[0][0], targets[0][1]) if targets else 0
    cur_opp = md(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue

        new_opp = md(nx, ny, ox, oy)
        if targets:
            new_res = min(md(nx, ny, tx, ty) for tx, ty in targets)
            res_gain = cur_res - new_res
        else:
            new_res = 0
            res_gain = 0

        score = res_gain * 2 - new_opp
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move