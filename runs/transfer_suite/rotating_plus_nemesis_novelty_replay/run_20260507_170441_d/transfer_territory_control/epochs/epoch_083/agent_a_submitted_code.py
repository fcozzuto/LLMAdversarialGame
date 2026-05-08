def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    my_cnt = int(observation.get("self_territory_count", len(my_t)) or len(my_t))
    op_cnt = int(observation.get("opponent_territory_count", len(op_t)) or len(op_t))
    attacker = my_cnt < op_cnt

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    cand_targets = []
    if resources:
        for p in resources:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in blocked:
                    cand_targets.append((x, y))
            except:
                pass
    if unclaimed:
        for p in unclaimed:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in blocked:
                    cand_targets.append((x, y))
            except:
                pass
    if not cand_targets:
        cand_targets = [(ox, oy)] if attacker else [(ox, oy), (sx, sy)]

    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    target = (ox, oy)
    if not attacker and cand_targets:
        best = None
        bestd = 10**9
        for tx, ty in cand_targets:
            d = man(sx, sy, tx, ty)
            if d < bestd or (d == bestd and (tx, ty) < best):
                bestd = d
                best = (tx, ty)
        target = best if best is not None else (ox, oy)
    elif attacker and cand_targets:
        best = None
        bestd = 10**9
        for tx, ty in cand_targets:
            d = man(ox, oy, tx, ty)
            if d < bestd or (d == bestd and (tx, ty) < best):
                bestd = d
                best = (tx, ty)
        if best is not None:
            target = best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = man(nx, ny, target[0], target[1])
        score = -d
        if (nx, ny) == (ox, oy):
            score += 1000
        if (dx, dy) != (0, 0):
            score += 1
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]