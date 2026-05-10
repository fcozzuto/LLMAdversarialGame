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

    best_dxdy = (0, 0)
    best = -10**18

    # Prefer claiming on our side while keeping away from the opponent; flip if it also increases safety.
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
        score += (3.4 if in_unc else 0.0)
        score += (2.2 if in_own else 0.0)
        score += (1.6 if in_opp else 0.0)

        # Safety: stay far from opponent (increases likelihood to secure territory).
        score += 0.010 * dist_op

        # Counter center-claim: prefer outer cells early-ish; shift slightly toward center later.
        t = float(observation.get("turn_index", 0) or 0)
        turns_rem = int(observation.get("turns_remaining", 0) or 0)
        prog = t / (t + turns_rem + 1.0)
        score += (0.012 * dist_center) * (1.0 - 0.6 * prog)

        # Mild bias to keep moving along a frontier rather than oscillating at one cell.
        score -= 0.002 * ((nx - sx) * (nx - sx) + (ny - sy) * (ny - sy))

        if score > best:
            best = score
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]