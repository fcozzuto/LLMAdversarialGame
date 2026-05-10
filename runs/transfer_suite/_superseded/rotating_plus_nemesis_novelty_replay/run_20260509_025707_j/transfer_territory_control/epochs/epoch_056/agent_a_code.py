def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_list = list(opp_set)
    if opp_list:
        ax, ay = sum(p[0] for p in opp_list) / len(opp_list), sum(p[1] for p in opp_list) / len(opp_list)
    else:
        ax, ay = (w - 1) / 2, (h - 1) / 2

    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        if (nx, ny) in opp_set:
            base = 4.0
        elif (nx, ny) in my_set:
            base = 0.7
        elif (nx, ny) in un_set:
            base = 1.6
        else:
            base = 0.9

        # Move toward opponent and away from our edge when we're leading
        myc = observation.get("self_territory_count", len(my_set))
        opc = observation.get("opponent_territory_count", len(opp_set))
        lead = 1.0 if myc > opc else 0.0

        dist_to_opp = manh(nx, ny, int(round(ax)), int(round(ay)))
        toward = -0.08 * dist_to_opp

        # Avoid stepping next to obstacles that can trap us; also prefer cutting into opp borders
        near_opp_border = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in opp_set:
                    near_opp_border += 1
        near_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in obstacles:
                    near_obs += 1

        edge_risk = 0.0
        if lead > 0.5:
            # when leading, don't rush into unknown; slightly penalize moves that are not our territory
            if (nx, ny) not in my_set:
                edge_risk -= 0.4

        score = base + toward + 0.35 * near_opp_border - 0.25 * near_obs + edge_risk

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer dx,dy closer to right/down (stable ordering)
            if (dx, dy) > (best[0], best[1]):
                best = [dx, dy]

    return [int(best[0]), int(best[1])]