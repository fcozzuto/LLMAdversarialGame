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

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def is_adj_to_opp(cell):
        x, y = cell
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in opp_t:
                    return True
        return False

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            cell = (nx, ny)

            score = 0
            if cell in opp_t:
                score += 6
            elif cell in self_t:
                score += 1
            elif cell in unclaimed:
                score += 3
                if is_adj_to_opp(cell):
                    score += 4

            # keep pressure while avoiding getting too close if no target
            dist_opp = d((nx, ny), (ox, oy))
            score += (8 - dist_opp) * 0.2

            # slight preference to expand territory toward opponent side
            score += (nx - sx) * 0.05 + (ny - sy) * 0.02

            candidates.append((score, -d((nx, ny), (ox, oy)), nx, ny, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [candidates[0][4], candidates[0][5]]