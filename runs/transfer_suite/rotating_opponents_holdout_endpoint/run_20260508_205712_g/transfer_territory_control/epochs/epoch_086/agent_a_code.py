def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_list = observation.get("opponent_territory") or []
    self_list = observation.get("self_territory") or []
    un_list = observation.get("unclaimed_cells") or []
    obs_list = observation.get("obstacles") or []

    opp_set = set()
    for p in opp_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))
    self_set = set()
    for p in self_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_set.add((x, y))
    un_set = set()
    for p in un_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                un_set.add((x, y))
    blocked = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    # Deterministic move preference order
    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    opp_count = int(observation.get("opponent_territory_count") or 0)
    un_count = len(un_set)
    self_corner_bias = (sx <= 1 or sy <= 1)  # start corner: prefer expanding outward
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        cell_score = 0
        if (nx, ny) in un_set:
            cell_score += 1200
            if un_count < 10:
                cell_score += 200
        elif (nx, ny) in opp_set:
            # Only raid if it advances toward the center and opponent is not too dominant
            d0 = abs(sx - cx) + abs(sy - cy)
            d1 = abs(nx - cx) + abs(ny - cy)
            cell_score += 850 if d1 < d0 else 250
            cell_score += 200 if opp_count < (w * h) // 2 else 0
        elif (nx, ny) in self_set:
            cell_score += 400
        else:
            # Unreachable/rare: unclaimed but not listed; keep neutral
            cell_score += 300

        # Frontier shaping: prefer moving away from edges that are already ours? Actually prefer filling diagonals outward.
        edge_pen = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            edge_pen -= 10 if self_corner_bias else 0
        cell_score += edge_pen

        # Avoid getting trapped: prefer closer to center when safe, but prioritize unclaimed
        d1 = abs(nx - cx) + abs(ny - cy)
        cell_score += (-2 * d1) if (nx, ny) in opp_set else (-1 * d1)

        # Slight preference for diagonal expansion when possible
        if dx != 0 and dy != 0:
            cell_score += 5

        if cell_score > best_score:
            best_score = cell_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]