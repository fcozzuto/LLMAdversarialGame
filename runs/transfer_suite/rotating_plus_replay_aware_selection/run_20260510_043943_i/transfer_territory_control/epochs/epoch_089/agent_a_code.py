def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_sp = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_sp[0]), int(opp_sp[1])

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                unclaimed.append((x, y))

    opp_terr = []
    opp_terr_set = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                opp_terr.append((x, y))
                opp_terr_set.add((x, y))

    self_tc = int(observation.get("self_territory_count") or 0)
    opp_tc = int(observation.get("opponent_territory_count") or 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    attack = self_tc < opp_tc
    want_target = bool(unclaimed) if not attack else (not unclaimed)  # if attacking, prefer opponent cells

    best_sc = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_un = 10**9
        if unclaimed:
            d_un = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in unclaimed)

        d_opp_terr = 10**9
        if opp_terr:
            d_opp_terr = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in opp_terr)

        d_opp_pos = abs(nx - ox) + abs(ny - oy)

        is_capture = (nx, ny) in opp_terr_set
        sc = 0.0

        if is_capture:
            sc += 1e6
            sc += 200.0 / (1 + d_opp_terr)
        if want_target:
            sc += 120.0 / (1 + d_un)
            sc -= 0.5 * d_opp_pos
        else:
            # Attack: move closer to opponent territory, but don't walk straight into obstacles (already handled)
            sc += 200.0 / (1 + d_opp_terr)
            sc -= 0.2 * d_un

        # Slight preference for expanding away from opponent position when not attacking
        if not attack and not is_capture:
            sc += 0.6 * d_opp_pos

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]