def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                opp_d = abs(ox - nx) + abs(oy - ny)
                if opp_d < (abs(ox - (sx + best[0])) + abs(oy - (sy + best[1]))) or best == [0, 0]:
                    best = [dx, dy]
        return best

    def score_target(tx, ty):
        sd = abs(sx - tx) + abs(sy - ty)
        od = abs(ox - tx) + abs(oy - ty)
        return (od - sd, -sd, -(abs(tx - ox) + abs(ty - oy)), -tx, -ty)

    tx, ty = max(resources, key=lambda p: score_target(p[0], p[1]))

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        ns = abs(nx - tx) + abs(ny - ty)
        os = abs(ox - nx) + abs(oy - ny)
        key = (os - ns, -ns, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]