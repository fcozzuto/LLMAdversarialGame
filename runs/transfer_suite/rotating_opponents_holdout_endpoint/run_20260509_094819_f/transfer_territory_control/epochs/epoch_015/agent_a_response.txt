def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    unclaimed_list = list(unclaimed)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_dist_to_set(x, y, s):
        if not s:
            return abs(x - ox) + abs(y - oy)
        md = 10**9
        for tx, ty in s:
            d = abs(x - tx) + abs(y - ty)
            if d < md:
                md = d
        return md

    def neighbor_opp_risk(x, y):
        # If we move into/adjacent to opponent territory, being there can be risky for counterclaim.
        best = 10**9
        for tx, ty in opp_terr:
            d = max(abs(x - tx), abs(y - ty))
            if d < best:
                best = d
                if best <= 1:
                    break
        return best

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**9
        dO = abs(x - ox) + abs(y - oy)
        dOppTerr = min_dist_to_set(x, y, opp_terr)
        cell = (x, y)
        if cell in opp_terr:
            # Prefer capturing opponent cells; closer to them gives larger swing.
            return 220 - 3 * dO - 20 * (dOppTerr > 0)
        if cell in unclaimed:
            # Prefer unclaimed near opponent to force expansion/contesting.
            return 90 - 2 * dOppTerr - dO // 2
        if cell in self_terr:
            # Hold territory; prefer moving toward fronts (near unclaimed/opp).
            # Encourage staying if opponent is far.
            front = 0
            if unclaimed_list:
                # approximate: use min dist to unclaimed only if small set
                if len(unclaimed_list) <= 10:
                    mdU = 10**9
                    for ux, uy in unclaimed_list:
                        d = abs(x - ux) + abs(y - uy)
                        if d < mdU:
                            mdU = d
                    front += 2 * (8 - min(mdU, 8))
            return 25 - dOppTerr // 2 - front - 3 * (neighbor_opp_risk(x, y) <= 1)
        # Empty/other: mild move toward opponent, avoid dead-ends behind obstacles
        return 10 - dO // 2 - 5 * (neighbor_opp_risk(x, y) <= 1)

    # Small deterministic reorientation: at even turns bias toward diagonals to break ties.
    bias = 1 if (observation.get("turn_index", 0) % 2 == 0) else -1
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_cell(nx, ny)
        if dx != 0 and dy != 0:
            v += bias * 0.5
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]