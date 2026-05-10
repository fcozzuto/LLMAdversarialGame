def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_list = list(opp_set)
    un_list = list(un_set)
    target_un = min(un_list, key=lambda p: (man((sx, sy), p), p[1], p[0])) if un_list else None
    target_opp = min(opp_list, key=lambda p: (man((sx, sy), p), p[1], p[0])) if opp_list else None

    best = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        val = 0.0

        if (nx, ny) in self_set:
            val -= 0.3
        if (nx, ny) in un_set:
            val += 12.0
        if (nx, ny) in opp_set:
            val += 18.0

        # Strategic preference: get closer to best unclaimed; if none, press opponent.
        if target_un is not None:
            val += 6.0 / (1 + man((nx, ny), target_un))
        if target_opp is not None:
            val += 5.0 / (1 + man((nx, ny), target_opp))

        # Border expansion: move next to our territory
        for ax, ay in neighbors8(nx, ny):
            if (ax, ay) in self_set:
                val += 1.0
            if (ax, ay) in opp_set:
                val += 0.7

        # Slight anti-stall unless we're already boxed
        if dx == 0 and dy == 0:
            val -= 1.0

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]