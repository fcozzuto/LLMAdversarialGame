def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    candidates = []
    for dx in dxs:
        for dy in dys:
            if abs(dx) + abs(dy) == 2:
                continue
            candidates.append((dx, dy))
    candidates = sorted(candidates, key=lambda t: (t[0], t[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (None, -10**9)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_from_center = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
        score = -2 * dist_to_opp - 0.05 * dist_from_center
        if (nx, ny) in opp_terr:
            score += 5.5
        elif (nx, ny) in unclaimed:
            score += 2.0
        elif (nx, ny) in self_terr:
            score += 0.5

        # Prefer moves that don't "stall" too much: align toward opponent if possible
        score += 0.6 * (1 if (dx == 0 and ((ny > sy) == (oy > sy)) ) or (dy == 0 and ((nx > sx) == (ox > sx))) else 0)

        # Slightly prefer staying still only if already surrounded
        if dx == 0 and dy == 0:
            score -= 1.0

        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]