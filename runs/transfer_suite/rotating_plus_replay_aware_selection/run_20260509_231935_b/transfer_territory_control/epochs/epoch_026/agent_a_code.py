def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = (opp_set and (sum(x for x, _ in opp_set) / len(opp_set), sum(y for _, y in opp_set) / len(opp_set))) or (w - 1, h - 1)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (float("-inf"), 0, 0)
    best_move = (0, 0)

    candidates = unclaimed if unclaimed else (list(opp_set) if opp_set else list(self_set))
    if not candidates:
        return [0, 0]

    def cell_priority(x, y):
        d = abs(x - sx) + abs(y - sy)
        to_opp = abs(x - ox) + abs(y - oy)
        to_center = abs(x - cx) + abs(y - cy)
        in_self = (x, y) in self_set
        in_opp = (x, y) in opp_set
        claimed = 1 if in_self else (2 if in_opp else 0)
        # Prefer unclaimed, but also press toward opponent center.
        return (-d, -(claimed), -to_opp, -to_center, x, y)

    # Deterministically choose best immediate step by evaluating best target each move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
            continue

        # Score based on best reachable target preference from (nx,ny).
        # Use only local computation to stay brief/deterministic.
        local_best = None
        for tx, ty in candidates[:40]:
            pr = cell_priority(tx, ty)
            # recompute distance part for the step (affects -d component)
            d = abs(tx - nx) + abs(ty - ny)
            pr2 = ( -d, pr[1], pr[2], pr[3], pr[4], pr[5] )
            if local_best is None or pr2 < local_best:
                local_best = pr2

        if local_best is None:
            continue

        # Convert priority to numeric score: lower pr2 is better; invert deterministically.
        score = (
            local_best[0] * -1.0
            + local_best[1] * 10.0
            + local_best[2] * 1.5
            + local_best[3] * 0.1
        )

        # Small tie-break: avoid stepping closer to obstacles' neighbors by discouraging risky edges.
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obs:
                    risk += 1
        score -= risk * 0.01

        key = (score, -dx, -dy)
        if key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]