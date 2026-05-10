def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2}

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = {(p[0], p[1]) for p in self_terr if p is not None and len(p) >= 2}
    opp_set = {(p[0], p[1]) for p in opp_terr if p is not None and len(p) >= 2}
    un_set = {(p[0], p[1]) for p in unclaimed if p is not None and len(p) >= 2}

    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))

    dxs = (-1, 0, 1)
    best = (None, -10**9, 0, 0)
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            if (nx, ny) in self_set:
                base = -20
            elif (nx, ny) in opp_set:
                base = -30
            elif (nx, ny) in un_set:
                base = 50 if myc <= opc else 40
            else:
                base = 5

            dist_opp = abs(nx - ox) + abs(ny - oy)
            dist_un = 0
            if un_set:
                # simple nearest-unclaimed estimate via distance to closest known unclaimed
                ux, uy = min(un_set, key=lambda p: abs(nx - p[0]) + abs(ny - p[1]))
                dist_un = abs(nx - ux) + abs(ny - uy)

            score = base
            if myc <= opc and un_set:
                score += 30 - dist_un
            else:
                score += (20 - dist_opp) * (1 if opc > myc else -1)

            # deterministic tie-break: smaller dx, then smaller dy
            key = (dx, dy)
            cand = (key, score, nx, ny)
            if cand[1] > best[1] or (cand[1] == best[1] and cand[0] < best[0]):
                best = cand

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]