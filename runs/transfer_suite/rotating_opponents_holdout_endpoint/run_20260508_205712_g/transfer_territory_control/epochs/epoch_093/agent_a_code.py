def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def parse(key):
        out = []
        for c in observation.get(key) or []:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    out.append((x, y))
        return out

    unclaimed = parse("unclaimed_cells")
    opp_t = parse("opponent_territory")
    our_t = parse("self_territory")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def score_target(tx, ty):
        d_me = max(abs(tx - sx), abs(ty - sy))
        d_opp = max(abs(tx - ox), abs(ty - oy))
        edge = (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1)
        base = 0
        if (tx, ty) in opp_t:
            base += 40  # flip pressure
        if edge:
            base += 12
        if (tx, ty) in unclaimed:
            base += 18
        # prefer closing advantage and not overcommitting to far targets
        return base + (d_opp - d_me) * 2 - d_me * 0.3

    # Candidate targets: prioritize edge unclaimed, then remaining unclaimed, then opponent territory
    edge_unclaimed = [(x, y) for (x, y) in unclaimed if x == 0 or x == w - 1 or y == 0 or y == h - 1]
    candidates = edge_unclaimed[:10] or unclaimed[:20] or opp_t[:20] or [(ox, oy)]

    best_cell = None
    best_val = -10**9
    for tx, ty in candidates:
        v = score_target(tx, ty)
        if v > best_val:
            best_val = v
            best_cell = (tx, ty)

    if best_cell is None:
        best_cell = (ox, oy)

    tx, ty = best_cell

    best_move = (0, 0)
    best_rank = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Prefer moves that reduce distance to target; slightly penalize moving into opponent territory too late
        d_new = max(abs(tx - nx), abs(ty - ny))
        d_old = max(abs(tx - sx), abs(ty - sy))
        closing = d_old - d_new
        into_opp = (nx, ny) in opp_t
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        # avoid oscillation: bias staying if already not improving
        rank = closing * 10 + (20 if into_opp else 0) + (4 if edge else 0) - (1 if (dx, dy) == (0, 0) else 0)
        if rank > best_rank:
            best_rank = rank
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]