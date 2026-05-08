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

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed if 0 <= int(x) < w and 0 <= int(y) < h]

    self_count = int(observation.get("self_territory_count", 0) or 0)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    aggressive = self_count <= opp_count

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in blocked:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = None
    best_score = None
    if aggressive or not unclaimed:
        for dx, dy, nx, ny in cand:
            dist = abs(nx - ox) + abs(ny - oy)
            score = (-dist, 0 if (nx, ny) == (sx, sy) else 1)
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]
    else:
        def closest_unclaimed_dist(nx, ny):
            md = None
            for ux, uy in unclaimed:
                d = abs(nx - ux) + abs(ny - uy)
                if md is None or d < md:
                    md = d
            return md if md is not None else 10**9

        for dx, dy, nx, ny in cand:
            d = closest_unclaimed_dist(nx, ny)
            score = (-d, -abs(nx - ox) - abs(ny - oy))
            if best_score is None or score > best_score:
                best_score, best = score, [dx, dy]

    if best is None:
        return [0, 0]
    return best