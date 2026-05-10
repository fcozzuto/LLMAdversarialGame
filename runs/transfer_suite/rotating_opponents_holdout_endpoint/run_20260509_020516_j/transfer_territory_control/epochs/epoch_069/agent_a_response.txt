def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    own = set(tuple(c) for c in (observation.get("self_territory") or []))
    opp = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in blocked:
            continue

        in_own = (nx, ny) in own
        in_opp = (nx, ny) in opp
        in_unc = (nx, ny) in unclaimed

        dist_op = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dist_center = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        score = 0.0
        if in_opp:
            score += 12.0  # prefer flipping opponent
        elif in_unc:
            score += 7.0   # prefer expanding into unclaimed
        elif in_own:
            score += 2.0   # maintain territory

        score += -0.12 * dist_op
        score += -0.03 * dist_center
        if dx == 0 and dy == 0:
            score -= 3.5  # discourage standing still

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]