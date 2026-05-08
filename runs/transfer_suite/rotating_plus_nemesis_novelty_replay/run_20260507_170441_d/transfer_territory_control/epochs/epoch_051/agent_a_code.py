def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def neigh_count(cell, target_set):
        x, y = cell
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in target_set:
                c += 1
        return c

    # Determine whether opponent is close; if yes, prioritize counter-claiming cells adjacent to them.
    opp_adj = neigh_count((sx, sy), opp_t)
    attack_mode = opp_adj >= 1

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cell = (nx, ny)
        score = 0.0

        # Immediate value for the cell we would control after entry (flip enabled).
        if cell in self_t:
            score += 1.0
        elif cell in unclaimed:
            score += 2.5
        elif cell in opp_t:
            score += 6.0
        else:
            score += 0.5

        # Frontier pressure: prefer cells next to opponent territory.
        adj_opp = neigh_count(cell, opp_t)
        adj_self = neigh_count(cell, self_t)
        if attack_mode:
            score += 3.0 * adj_opp
            score += -1.0 * (adj_self)
        else:
            score += 2.0 * adj_opp
            score += 1.5 * adj_self

        # Keep expanding toward center to avoid being boxed in.
        dist_center = abs(nx - cx) + abs(ny - cy)
        score += -0.05 * dist_center

        # If opponent is near, also move to reduce distance between them and our front.
        if attack_mode:
            score += -0.10 * (abs(nx - ox) + abs(ny - oy))
        else:
            # Otherwise, avoid walking directly into their trail when we don't need to.
            if cell in opp_t:
                score += 0.8

        # Deterministic tie-break: fixed dir order.
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]