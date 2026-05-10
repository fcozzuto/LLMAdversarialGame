def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_cells(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    best = (0, 0)
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cell = (nx, ny)

        # Base value by ownership
        if cell in opp_t:
            sc = 7.0
        elif cell in self_t:
            sc = 0.8
        elif cell in unclaimed:
            sc = 2.3
        else:
            sc = 0.1

        # Expansion and contest signals
        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for ax, ay in adj_cells(nx, ny):
            a = (ax, ay)
            if a in unclaimed:
                adj_un += 1
            elif a in opp_t:
                adj_opp += 1
            elif a in self_t:
                adj_self += 1

        sc += 0.35 * adj_un
        sc += 0.20 * adj_self

        # Avoid stepping into "duel" adjacent-to-opponent zones unless capturing directly
        if cell not in opp_t and adj_opp > 0:
            sc -= 0.9 * adj_opp

        # If we can capture opponent territory, prioritize edge-contact
        if cell in opp_t:
            sc += 0.35 * adj_opp

        # Soft preference to move away from closest obstacle proximity isn't available; deterministic tie-break only
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]