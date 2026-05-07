def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    blocked = set()
    for ob in observation.get("obstacles") or []:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
        elif isinstance(ob, dict):
            if "x" in ob and "y" in ob:
                x, y = int(ob["x"]), int(ob["y"])
            else:
                p = ob.get("position")
                if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                    continue
                x, y = int(p[0]), int(p[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def parse_cell(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict) and "x" in r and "y" in r:
            return int(r["x"]), int(r["y"])
        if isinstance(r, dict) and "position" in r:
            p = r["position"]
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return None

    targets = []
    for r in resources:
        c = parse_cell(r)
        if c is None:
            continue
        if c in blocked:
            continue
        d_my = dist(my_pos, c)
        d_op = dist(op_pos, c)
        advantage = d_op - d_my  # positive means we're closer
        tie = d_my
        targets.append((-(advantage), tie, c))
    if not targets:
        return [0, 0]

    targets.sort()
    chosen = targets[0][2]

    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            my_next = (nx, ny)
            d_my_next = dist(my_next, chosen)
            d_my_now = dist(my_pos, chosen)
            d_op_now = dist(op_pos, chosen)

            # Prefer moves that bring us closer; when tied, maximize relative closeness vs opponent.
            score = (-(d_my_next - d_my_now), (d_op_now - d_my_next), -(abs(nx - ox) + abs(ny - oy)))
            if best is None or score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]