def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_cells = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_cells.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    targets = resources if resources else unclaimed
    if not targets:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = None
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_cells:
            continue

        flip_bonus = 0
        if (nx, ny) in opp_terr:
            flip_bonus = 25 + abs(ox - nx) + abs(oy - ny)

        # "Win" nearby territory: prefer moves that secure a cell closer to us than to opponent,
        # and that reduce opponent's access.
        best_cell_margin = -10**9
        closest_gain = 10**9
        for tx, ty in targets[:18]:
            sd = abs(tx - nx) + abs(ty - ny)
            od = abs(tx - ox) + abs(ty - oy)
            margin = od - sd  # positive => we are nearer
            if margin > best_cell_margin:
                best_cell_margin = margin
            if sd < closest_gain:
                closest_gain = sd

        opp_dist_now = abs(ox - nx) + abs(oy - ny)
        self_dist_to_opp = abs(ox - sx) + abs(oy - sy)
        pursuit = (self_dist_to_opp - opp_dist_now)  # positive means we move closer

        val = flip_bonus + 2.2 * best_cell_margin - 0.9 * closest_gain + 0.35 * pursuit
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]