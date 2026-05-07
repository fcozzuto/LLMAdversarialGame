def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    rem = int(observation.get("remaining_resource_count", len(res)) or len(res))
    if rem <= 4:
        endgame = 2.2
    elif rem <= 8:
        endgame = 1.35
    else:
        endgame = 1.05

    # Pick a target deterministically: maximize advantage for collecting first.
    best = None
    best_score = -10**18
    for x, y in res:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        # Encourage grabbing when opponent is slower; slightly prefer closer target overall.
        adv = od - sd  # positive => we are closer
        score = (adv * (12.0 * endgame)) - (0.20 * sd) + (1.0 / (1.0 + sd))
        # If distances are tied, prefer the one we can arrive with fewer steps that also reduces opponent pressure.
        score += (-0.01 * abs(od - sd))
        if score > best_score:
            best_score = score
            best = (x, y)
    tx, ty = best

    # Choose best one-step move that approaches target while avoiding obstacles.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    # Deterministic tie-break order: keep as defined above.

    best_m = (0, 0)
    best_m_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sd2 = abs(tx - nx) + abs(ty - ny)
        sd_now = abs(tx - sx) + abs(ty - sy)
        # Main: decrease distance to target. Secondary: avoid moving to squares that make us easy to deny.
        # Also slight preference to not fall behind if opponent is already closer.
        opp_d = abs(tx - ox) + abs(ty - oy)
        behind_pen = 0.0
        if sd2 > opp_d:
            behind_pen = -6.0 * (sd2 - opp_d)

        # If we're already on the target (resource), prefer staying (collect).
        on_target = 1.0 if (sx == tx and sy == ty) else 0.0

        move_score = (sd_now - sd2) * (18.0 * endgame) - (0.05 * sd2) + behind_pen + on_target
        if move_score > best_m_score:
            best_m_score = move_score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]