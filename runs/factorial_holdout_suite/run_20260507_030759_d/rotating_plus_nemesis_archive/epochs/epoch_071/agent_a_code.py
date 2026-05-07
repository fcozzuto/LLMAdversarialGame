def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a >= b else b

    def best_target():
        if not resources:
            return (w // 2, h // 2)
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prioritize denying opponent (large do-ds), then grabbing faster (small ds)
            key = (do - ds, -ds, -(rx + ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = best_target()
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue
        nds = cheb(nx, ny, tx, ty)
        # estimate opponent "pressure" if we go elsewhere: prefer smaller ds and also not giving opponent too much advantage
        opp_adv = cur_do - cheb(ox, oy, tx, ty)  # 0; keep deterministic structure
        # opponent likely goes nearest resource; but we can only influence via denying: measure how much our move reduces the gap
        gap_before = cur_do - cur_ds
        gap_after = cur_do - nds
        score = (gap_after, -(nds), -(abs((tx - nx)) + abs((ty - ny))), -opp_adv, -((dx != 0) + (dy != 0)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_score is None:
        # all blocked: stay still
        return [0, 0]
    return best_move