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

    if opp_t:
        ax = sum(x for x, _ in opp_t) / len(opp_t)
        ay = sum(y for _, y in opp_t) / len(opp_t)
        cx, cy = int(round(ax)), int(round(ay))
    else:
        cx, cy = w // 2, h // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh8 = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    aggressiveness = 1.0 if (observation.get("opponent_territory_count", len(opp_t)) or 0) > (observation.get("self_territory_count", len(self_t)) or 0) else 0.6

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            candidates.append((-(10**9), dx, dy))
            continue
        is_opp = (nx, ny) in opp_t
        is_un = (nx, ny) in unclaimed
        d_to_center = abs(nx - cx) + abs(ny - cy)

        adj_opp = 0
        for ddx, ddy in neigh8:
            if (nx + ddx, ny + ddy) in opp_t:
                adj_opp += 1
        adj_unclaimed = 0
        for ddx, ddy in neigh8:
            if (nx + ddx, ny + ddy) in unclaimed:
                adj_unclaimed += 1

        score = 0
        score += (1200 * aggressiveness) if is_opp else 0
        score += (200 if is_un else 0)
        score += (35 * adj_opp) + (10 * adj_unclaimed)
        score += (-1.2 * d_to_center)
        score += (0.5 * (1 - (abs(nx - ox) + abs(ny - oy)) / (w + h)))
        candidates.append((score, dx, dy))

    candidates.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2]), -t[1], -t[2]), reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]