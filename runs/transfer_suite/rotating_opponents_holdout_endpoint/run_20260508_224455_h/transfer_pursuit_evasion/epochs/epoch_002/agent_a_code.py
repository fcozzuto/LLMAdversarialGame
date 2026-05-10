def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    self_role = str(observation.get("self_role", "")).lower()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    i_am_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if "evader" in self_role or "evade" in self_role:
        i_am_pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if i_am_pursuer:
            score = -d2  # maximize closeness
        else:
            score = d2  # maximize distance
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            if (dx, dy) == (0, 0):
                continue
            # deterministic tie-breaker: prefer non-stay, then smallest dx, then smallest dy
            if best == (0, 0) or (dx, dy)[0] < best[0] or ((dx, dy)[0] == best[0] and (dx, dy)[1] < best[1]):
                best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]