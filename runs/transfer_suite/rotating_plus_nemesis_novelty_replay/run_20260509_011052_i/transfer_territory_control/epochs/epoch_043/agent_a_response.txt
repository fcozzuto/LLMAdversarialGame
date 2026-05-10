def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def dist_to_nearest(a, B):
        if not B:
            return 10**9
        ax, ay = a
        best = 10**9
        for bx, by in B:
            d = abs(bx - ax) + abs(by - ay)
            if d < best: best = d
        return best

    un_list = list(unclaimed)
    opp_list = list(opp_terr) if opp_terr else [(ox, oy)]

    def adj_cnt(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    lead = observation.get("self_territory_count", 0) - observation.get("opponent_territory_count", 0)
    attack_mode = 1 if lead <= 2 else 0  # if not safely ahead, prioritize counterclaim

    best = None
    best_sc = -10**18
    # deterministic tie-break by fixed dir order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in unclaimed:
            sc += 6
            sc += 0.7 * adj_cnt(nx, ny, self_terr)
            sc += 0.3 * adj_cnt(nx, ny, opp_terr)
        elif (nx, ny) in self_terr:
            sc += 1.2 * adj_cnt(nx, ny, self_terr) + 0.3
        elif (nx, ny) in opp_terr:
            # flip on entry: only worth it if it increases frontier pressure
            sc += 10 if attack_mode else 7
            sc += 0.6 * adj_cnt(nx, ny, opp_terr)
            sc += 1.0 * adj_cnt(nx, ny, self_terr)
            sc -= 0.2 * (abs(ox - nx) + abs(oy - ny))
        else:
            sc += 0.1  # empty/unknown

        # always prefer approaching unclaimed near our direction/front
        if un_list:
            sc += 0.9 * (1.0 / (1 + dist_to_nearest((nx, ny), un_list)))
        # also prefer getting closer to opponent when attacking; otherwise, reduce contact
        dopp = abs(ox - nx) + abs(oy - ny)
        dcur = abs(ox - sx) + abs(oy - sy)
        sc += (1.2 if attack_mode else -0.4) * (dcur - dopp)

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]