def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                blocked.add((x, y))

    unclaimed = []
    for t in observation.get("unclaimed_cells") or []:
        if t is not None and len(t) >= 2:
            unclaimed.append((int(t[0]), int(t[1])))

    oppT = []
    for t in observation.get("opponent_territory") or []:
        if t is not None and len(t) >= 2:
            oppT.append((int(t[0]), int(t[1])))

    selfT = set()
    for t in observation.get("self_territory") or []:
        if t is not None and len(t) >= 2:
            selfT.add((int(t[0]), int(t[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        best_target = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif oppT:
        best_target = min(oppT, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), -t[0], -t[1]))
    else:
        best_target = (ox, oy)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue

        dist_to_target = abs(nx - tx) + abs(ny - ty)
        score = dist_to_target

        # Prefer expanding into unclaimed (and opponent territory) deterministically
        if (nx, ny) in selfT:
            score += 2.0  # slight penalty for staying within our territory

        # If flipping opponent territory is on entry, treat it as attractive
        if oppT and (nx, ny) in set(oppT):
            score -= 1.5

        # Avoid getting too close to opponent unless we're targeting nearby cells
        dist_to_op = abs(nx - ox) + abs(ny - oy)
        if dist_to_op <= 1:
            score += 3.0

        # Deterministic tie-break: favor moves with smaller |dx| then smaller |dy| then lexical
        score_key = (score, abs(dx), abs(dy), dx, dy)
        if score_key < (best_score, abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]