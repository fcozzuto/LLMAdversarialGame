def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                x, y = int(p.get("x", 0)), int(p.get("y", 0))
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))
        except Exception:
            pass

    self_tr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_tr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    dirs8 = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs = dirs8 + [(0, 0)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def opp_adj_count(cell):
        x, y = cell
        cnt = 0
        for dx, dy in dirs8:
            if (x + dx, y + dy) in opp_tr:
                cnt += 1
        return cnt

    # Lead -> defend some; behind -> attack more
    sc_s = int(observation.get("self_territory_count") or 0)
    sc_o = int(observation.get("opponent_territory_count") or 0)
    behind = 1 if sc_s < sc_o else 0
    attack_bias = 1.8 if behind else 1.0

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)
        if cell in opp_tr:
            val = 1e6 * attack_bias + 50 * opp_adj_count(cell) - (abs(nx - ox) + abs(ny - oy))
        elif cell in unclaimed:
            val = 300 * opp_adj_count(cell) * attack_bias + 30 * (W + H - (abs(nx - ox) + abs(ny - oy))) * (0.7 if behind else 1.0)
            val -= 20 * (cell in self_tr)
        elif cell in self_tr:
            # Prefer edges near opponent and slightly prefer reducing distance to opponent when tied
            val = 40 * opp_adj_count(cell) * (1.0 if not behind else 0.6) + (5 if (nx, ny) in self_tr else 0)
            val -= 2 * (abs(nx - ox) + abs(ny - oy)) * (0.2 if not behind else 0.6)
        else:
            val = -10**6  # shouldn't happen, but keep deterministic

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]