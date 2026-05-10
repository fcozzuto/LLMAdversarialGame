def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_lead = up >= op

    oxs = [x for x, y in op_terr]
    oys = [y for x, y in op_terr]
    if oxs:
        ocx = sum(oxs) / float(len(oxs))
        ocy = sum(oys) / float(len(oys))
    else:
        ocx, ocy = (w - 1) / 2.0, (h - 1) / 2.0

    targets = unclaimed if unclaimed else (op_terr if op_terr else set())
    if not targets:
        return [0, 0]

    best_t = None
    best_key = None
    lead_bias = 1.6 if we_lead else 0.0
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        dop = abs(tx - ocx) + abs(ty - ocy)
        key = (d + (-lead_bias * dop), tx, ty)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in unclaimed
        is_opp = (nx, ny) in op_terr
        is_self = (nx, ny) in self_terr

        dist = abs(nx - tx) + abs(ny - ty)
        d_target = abs(sx - tx) + abs(sy - ty)

        score = 0
        if is_un:
            score += 220
        if is_opp:
            score += 120 if not we_lead else 80
        if is_self:
            score += 20

        score += (d_target - dist) * 10  # prefer moving closer to target
        score += 3 * (abs(nx - ocx) + abs(ny - ocy) - (abs(sx - ocx) + abs(sy - ocy))) * (1.0 if we_lead else -0.2)

        # small deterministic preference to reduce stalling
        score += -1 if (dx == 0 and dy == 0) else 0

        key = (-score, dx, dy)
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]