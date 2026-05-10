def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    blocked = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed_set.add((int(p[0]), int(p[1])))
    opp_set = set()
    for p in opp_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        # deterministic priority: claim unclaimed, also progress toward center, and avoid overcommit near opponent
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_unclaimed = 10**9
        if unclaimed_set:
            for tx, ty in unclaimed_set:
                d = abs(tx - nx) + abs(ty - ny)
                if d < d_unclaimed:
                    d_unclaimed = d

        val = 0
        if (nx, ny) in unclaimed_set:
            val += 2000
        if (nx, ny) in opp_set:
            # flipping on entry is allowed; only do it if it also improves access (heuristic: closer to unclaimed)
            val += 400 if unclaimed_set else 0
        val += -3.0 * d_center
        if unclaimed_set:
            val += -1.5 * d_unclaimed
        val += 0.2 * d_opp  # keep some distance to reduce opponent contest pressure

        # slight bias to continue straight lines (deterministic tie-breaker)
        if dx == 0 and dy == 0:
            val -= 1.0
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]