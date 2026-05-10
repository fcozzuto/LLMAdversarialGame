def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obstacles = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    blocked = set((int(p[0]), int(p[1])) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer immediate expansion into adjacent unclaimed cells
    adj_targets = []
    for (tx, ty) in self_set:
        for dx, dy in dirs:
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed_set:
                adj_targets.append((nx, ny))
    if not adj_targets:
        # Otherwise push to edge/corner unclaimed to limit counterclaims
        adj_targets = [(cx, cy) for (cx, cy) in unclaimed_set
                        if cx in (0, w - 1) or cy in (0, h - 1)]
        if not adj_targets:
            adj_targets = list(unclaimed_set)
    if not adj_targets:
        return [0, 0]

    def cell_score(cx, cy):
        # Lower distance is better; edge is a bit better; avoid obstacles already handled
        d = abs(cx - x) + abs(cy - y)
        edge_bonus = 2 if (cx in (0, w - 1) or cy in (0, h - 1)) else 0
        # Allow entering opponent cells only if target is near; flipping can be worth it
        opp_penalty = 1 if (cx, cy) in opp_set else 0
        return -(d + opp_penalty) + edge_bonus * 0.1

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        # Heuristic: maximize best target reachable/approached
        # Compute best nearby target score after move
        move_val = - (abs(nx - x) + abs(ny - y)) * 0.01
        best_t = -10**18
        for (tx, ty) in adj_targets:
            # Prefer targets that would be closer after this move
            cur_d = abs(tx - x) + abs(ty - y)
            nxt_d = abs(tx - nx) + abs(ty - ny)
            if nxt_d > cur_d + 2:
                continue
            tval = cell_score(tx, ty) - (nxt_d * 0.05)
            best_t = tval if tval > best_t else best_t
        move_val += best_t if best_t > -10**18 else cell_score(nx, ny)
        # Small bias to not step into opponent unless it improves immediate expansion
        if (nx, ny) in opp_set:
            move_val -= 0.25
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]