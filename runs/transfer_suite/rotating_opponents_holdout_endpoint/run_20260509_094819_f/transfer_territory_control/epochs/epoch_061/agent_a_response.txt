def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) == 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) == 2:
            unclaimed.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_frontier(x, y):
        for dx, dy in dirs:
            if (x + dx, y + dy) in self_t:
                return True
        return False

    def cell_value(x, y):
        if (x, y) in obstacles:
            return -10**9
        v = 0
        if (x, y) in self_t:
            v += 2
        elif (x, y) in unclaimed:
            v += 10
        elif (x, y) in opp_t:
            v += 7
        else:
            v += 1
        if adj_frontier(x, y):
            v += 6
        # Prefer pushing away from opponent to reduce their sweeping advantage
        v += (abs(x - ox) + abs(y - oy)) * 0.03
        # Prefer not wasting steps far from own territory (keep expansion coherent)
        v -= min(abs(x - tx) + abs(y - ty) for (tx, ty) in self_t) * 0.02 if self_t else 0
        # Mild preference to approach nearest unclaimed when no frontier move exists
        if unclaimed:
            v += -min(abs(x - ux) + abs(y - uy) for (ux, uy) in unclaimed) * 0.01
        return v

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        val = cell_value(nx, ny)
        if val > best[0] or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]