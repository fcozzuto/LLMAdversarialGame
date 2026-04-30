def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    def eval_cell(nx, ny):
        if (nx, ny) in obst:
            return -10**18
        dres = 0
        if res:
            dres = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in res)
        else:
            dres = abs(nx - w // 2) + abs(ny - h // 2)
        dop = abs(nx - ox) + abs(ny - oy)
        return (-10 * dres) + (dop if res else 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            score = eval_cell(nx, ny)
            if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    dx, dy = best
    return [dx, dy]