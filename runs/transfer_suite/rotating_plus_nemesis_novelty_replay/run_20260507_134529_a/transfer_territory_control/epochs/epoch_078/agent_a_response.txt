def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_value(x, y):
        # Territory control: aggressive, but prefer safe expansion when not much opp territory is adjacent.
        if (x, y) in obstacles:
            return -10_000.0
        if (x, y) in opp_terr:
            base = 6.0
        elif (x, y) in unclaimed:
            base = 2.4
        elif (x, y) in self_terr:
            base = 0.8
        else:
            base = 0.3
        if (x, y) in resources:
            base += 2.0
        # Extra drive: move toward opponent and toward frontier cells near opponent territory.
        if opp_terr:
            man_opp = min(abs(x - ax) + abs(y - ay) for (ax, ay) in opp_terr)
            base += 1.2 * max(0, 6 - man_opp) / 6.0
            # If you are adjacent to their territory, reward capturing entry.
            if man_opp == 1:
                base += 1.5
        # Discourage stepping into our own enclosed corner when opponent is near (adds stability).
        man_from_opp_pos = abs(x - ox) + abs(y - oy)
        base += 0.15 if man_from_opp_pos <= 2 else 0.0
        return base

    best = None
    best_v = -1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = cell_value(nx, ny)
            # Tie-breaker: deterministic prefer diagonal/forward toward opponent quadrant.
            if (nx, ny) == (sx, sy):
                v -= 0.05
            if dx != 0 and dy != 0:
                v += 0.01
            if ox > sx and nx > sx:
                v += 0.005
            elif ox < sx and nx < sx:
                v += 0.005
            if v > best_v:
                best_v = v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]