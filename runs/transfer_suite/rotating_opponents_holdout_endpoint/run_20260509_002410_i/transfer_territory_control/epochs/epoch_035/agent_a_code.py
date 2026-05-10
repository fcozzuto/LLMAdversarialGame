def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        yield nx, ny

    if not inside(sx, sy):
        sx, sy = 0, 0

    move_options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None

    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0.0
        if (nx, ny) in opp_t:
            gain += 6.0
        elif (nx, ny) in unclaimed:
            gain += 3.5
        elif (nx, ny) in self_t:
            gain += 1.0

        opp_adj = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in opp_t:
                opp_adj += 1
        gain += 0.7 * opp_adj

        self_adj = 0
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in self_t:
                self_adj += 1
        gain += 0.15 * self_adj

        # Mild preference for moving (avoid getting stuck)
        dist = abs(nx - 0) + abs(ny - 0)
        gain += 0.001 * dist

        # Deterministic tie-break
        key = (gain, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]