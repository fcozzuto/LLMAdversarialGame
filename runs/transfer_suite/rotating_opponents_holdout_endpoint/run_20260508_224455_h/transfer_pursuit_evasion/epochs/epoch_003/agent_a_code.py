def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    self_role = str(observation.get("self_role", "")).lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if "evader" in self_role or "evade" in self_role:
        i_am_pursuer = False

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    prefix = (1 if i_am_pursuer else -1)

    sdx = 0 if ox == sx else (1 if ox > sx else -1)
    sdy = 0 if oy == sy else (1 if oy > sy else -1)

    def mobility(x, y):
        c = 0
        for a, b in moves:
            nx, ny = x + a, y + b
            if inb(nx, ny) and not blocked(nx, ny):
                c += 1
        return c

    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        aligned = abs(dx - sdx) + abs(dy - sdy)  # 0 is most aligned with direct pursuit/escape
        mob = mobility(nx, ny)
        # pursuer prefers smaller distance; evader prefers larger distance; both prefer higher mobility and alignment
        score = prefix * (-d2)  # pursuer: +(-d2), evader: -(-d2) => pursuer maximizes -d2, evader maximizes d2
        score += 0.15 * mob
        score += -0.05 * aligned
        # deterministic tie-breaker
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]