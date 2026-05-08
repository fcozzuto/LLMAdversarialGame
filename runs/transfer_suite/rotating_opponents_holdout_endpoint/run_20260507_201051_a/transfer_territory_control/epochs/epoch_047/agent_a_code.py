def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    opp_adj = set()
    for (x, y) in opp_t:
        for dx, dy in neighbors[:8]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in opp_t:
                opp_adj.add((nx, ny))

    candidates = []
    if unclaimed:
        for t in unclaimed:
            if t in opp_adj:
                candidates.append(t)
        if len(candidates) < 3:
            candidates += list(unclaimed)
    if not candidates:
        # fallback: go toward opponent-adjacent squares, else unclaimed, else center
        if opp_adj:
            candidates = list(opp_adj)
        elif unclaimed:
            candidates = list(unclaimed)
        else:
            candidates = [(w - 1) // 2, (h - 1) // 2]
            candidates = [(candidates[0], candidates[1])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def score_cell(x, y):
        # prioritize immediate counterclaim opportunities, then expansion near opponent,
        # then general expansion/center.
        d_to_opp = abs(x - ox) + abs(y - oy)
        in_opp = 1 if (x, y) in opp_t else 0
        in_self = 1 if (x, y) in self_t else 0
        d_center = abs(x - cx) + abs(y - cy)
        # Prefer: not already ours (to gain new), but allow flipping opponent territory.
        # High flip/pressure if adjacent to opponent territory.
        near_opp = 1 if (x, y) in opp_adj else 0
        return (200 * near_opp) + (120 * in_opp) + (30 * (1 - in_self)) - (2.2 * d_to_opp) - (0.7 * d_center)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in neighbors:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # evaluate by best target we can reach in one step (greedy)
        local = -10**18
        for t in candidates[:25]:
            tx, ty = t
            # movement cost plus cell quality; also reward moving closer to target.
            mv = abs(tx - nx) + abs(ty - ny)
            local = max(local, score_cell(tx, ty) - 1.1 * mv)
        # tie-break deterministically: prefer staying if equal, else smallest dx, then dy
        val = local
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]