def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (7, 7))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_list = list(opp_terr) if opp_terr else []
    self_count = int(observation.get("self_territory_count", 0) or 0)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    aggressive = self_count <= opp_count

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    def mindist_to_opp(px, py):
        if not opp_list:
            return abs(px - ox) + abs(py - oy)
        md = 10**9
        for tx, ty in opp_list:
            d = abs(px - tx) + abs(py - ty)
            if d < md:
                md = d
        return md

    # Main idea: edge-counter-claim. Move to either (a) opponent territory to flip, or (b) unclaimed cells
    # that are closest to opponent territory, while keeping some distance from the opponent when not aggressive.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = mindist_to_opp(nx, ny)
        cell_score = 0.0
        if (nx, ny) in opp_terr:
            cell_score += 5.0
        elif (nx, ny) in unclaimed:
            cell_score += 2.0
        elif (nx, ny) in self_terr:
            cell_score += 0.8

        # Prefer reducing distance to opponent territory edge.
        cell_score += max(0.0, 4.0 - d_opp) * (1.0 if aggressive else 0.8)

        # Anti-zerg: if not aggressive, avoid getting too close unless capturing opp territory.
        d_to_agent = abs(nx - ox) + abs(ny - oy)
        if aggressive:
            cell_score += max(0.0, 3.0 - d_to_agent) * 0.2
        else:
            cell_score += -max(0.0, 3.0 - d_to_agent) * (0.25 if (nx, ny) not in opp_terr else -0.05)

        # Slight preference to keep toward center to avoid corner-pinning vs edge claim.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        cell_score += -0.03 * dist_center

        key = (cell_score, -abs(dx) - abs(dy), dx, dy)
        if best is None or key > best_key:
            best = [dx, dy]
            best_key = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]