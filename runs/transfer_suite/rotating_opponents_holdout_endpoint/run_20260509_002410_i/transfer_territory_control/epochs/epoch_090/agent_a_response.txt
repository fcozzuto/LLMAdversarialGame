def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    unclaimed = observation.get("unclaimed_cells") or []
    if unclaimed:
        best = None
        for t in unclaimed:
            tx, ty = int(t[0]), int(t[1])
            dps = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
            dpc = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
            # Prefer unclaimed near center but reachable; tie-break deterministically
            score = dps + 0.35 * dpc + 0.001 * (ty * w + tx)
            if best is None or score < best[0]:
                best = (score, tx, ty)
        _, tx, ty = best
    else:
        opp_t = observation.get("opponent_territory") or []
        if not opp_t:
            tx, ty = int(w - 1 - sx), int(h - 1 - sy)
        else:
            # Target opposite-side of center relative to our position, biased to disrupt opponent
            best = None
            for t in opp_t:
                tx0, ty0 = int(t[0]), int(t[1])
                dps = (tx0 - sx) * (tx0 - sx) + (ty0 - sy) * (ty0 - sy)
                dpc = (tx0 - cx) * (tx0 - cx) + (ty0 - cy) * (ty0 - cy)
                score = dps - 0.25 * dpc + 0.001 * (ty0 * w + tx0)
                if best is None or score < best[0]:
                    best = (score, tx0, ty0)
            _, tx, ty = best

    # Choose neighbor that minimizes distance to target
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]