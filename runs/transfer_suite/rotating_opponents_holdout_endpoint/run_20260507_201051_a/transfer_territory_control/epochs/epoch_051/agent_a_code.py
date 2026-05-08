def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_set(x, y, s):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in s:
                    return True
        return False

    def mindist_to_set(x, y, s):
        if not s:
            return 99
        best = 99
        for px, py in s:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        val = 0
        if (nx, ny) in opp_t:
            val -= 1000
        if (nx, ny) in unclaimed:
            val += 14
        if (nx, ny) in self_t:
            val += 6

        if adj_set(nx, ny, self_t):
            val += 8  # expand/maintain our shape
        if adj_set(nx, ny, opp_t):
            val -= 18  # avoid counterclaims on contact

        od = mindist_to_set(nx, ny, opp_t)
        val += od * 2  # prefer staying far from opponent

        if (nx, ny) == (sx, sy):
            val -= 3  # discourage dithering unless forced

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]