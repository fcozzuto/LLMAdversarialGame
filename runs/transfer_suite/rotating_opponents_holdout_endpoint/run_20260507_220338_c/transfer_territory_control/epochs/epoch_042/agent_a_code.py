def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        try:
            obs_set.add((int(p[0]), int(p[1])))
        except:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    self_ter = observation.get("self_territory") or []
    opp_ter = observation.get("opponent_territory") or []
    self_set = set()
    opp_set = set()
    for p in self_ter:
        try:
            self_set.add((int(p[0]), int(p[1])))
        except:
            pass
    for p in opp_ter:
        try:
            opp_set.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    unc_set = set()
    for p in unclaimed:
        try:
            unc_set.add((int(p[0]), int(p[1])))
        except:
            pass

    sc = observation.get("self_territory_count", len(self_set)) or len(self_set)
    oc = observation.get("opponent_territory_count", len(opp_set)) or len(opp_set)

    center = (w // 2, h // 2)
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    best = None
    best_key = None
    toward_flip = sc < oc

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                nx, ny = sx, sy
                dx, dy = 0, 0
            cell = (nx, ny)

            if cell in self_set:
                base = 0.1
            elif cell in opp_set:
                base = 3.0 if toward_flip else 2.0
            elif cell in unc_set:
                base = 1.5 if not toward_flip else 1.2
            else:
                base = 0.0

            dist_opp = abs(nx - ox) + abs(ny - oy)
            dist_ctr = abs(nx - center[0]) + abs(ny - center[1])

            # Avoid giving opponent immediate access: prefer increasing distance from opponent
            # but still allow central capture if we are behind.
            opp_term = (dist_opp * (1.2 if toward_flip else 0.9)) - (dist_ctr * (0.35 if toward_flip else 0.55))

            key = (base + opp_term, -dist_ctr, dist_opp, -nx, -ny, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)

    return [int(best[0]), int(best[1])]