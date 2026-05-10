def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obstacles.add((int(p[0]), int(p[1])))

    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un_set = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    turn = int(observation.get("turn_index", 0) or 0)

    # If we're behind, prioritize flipping/claiming; if ahead, consolidate and cut off.
    behind = (int(observation.get("self_territory_count") or 0) < int(observation.get("opponent_territory_count") or 0))
    opp_bias = 1.0 if behind else 0.55
    early = turn < 10

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        is_un = (nx, ny) in un_set
        is_opp = (nx, ny) in opp_set
        is_self = (nx, ny) in self_set

        # Base priority
        if is_un:
            pr = 80
        elif is_opp:
            pr = 95 if (early or behind) else 70
        elif is_self:
            pr = 25 if not behind else 18
        else:
            pr = 5

        # Distance progress toward opponent and toward frontier near opponent
        d_op_prev = abs(sx - ox) + abs(sy - oy)
        d_op_new = abs(nx - ox) + abs(ny - oy)
        prog = d_op_prev - d_op_new  # higher is better

        # Also prefer moving to cells with more "unclaimed" neighbor exposure
        un_adj = 0
        # Small, deterministic local check (up to 4 orthogonals)
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in un_set:
                un_adj += 1

        # Tie-breaker: slightly prefer toward center to reduce opponent containment failure
        cx, cy = (w - 1) // 2, (h - 1) // 2
        cen = (abs(nx - cx) + abs(ny - cy)) * (-0.1 if behind else -0.03)

        score = pr + opp_bias * (prog * 10) + (un_adj * 2) + cen
        cand = (score, dx, dy)
        if cand > best:
            best = cand

    return [int(best[1]), int(best[2])]