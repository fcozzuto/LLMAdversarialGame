def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_center = (ox, oy)
    if opp_cells:
        sx2 = sum(x for x, _ in opp_cells)
        sy2 = sum(y for _, y in opp_cells)
        n = len(opp_cells)
        opp_center = (sx2 // n, sy2 // n)

    target = None
    if unclaimed:
        frontier = []
        for x, y in unclaimed:
            for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                nx, ny = x - dx, y - dy
                if (nx, ny) in self_cells:
                    frontier.append((x, y))
                    break
        cand = frontier if frontier else unclaimed
        tx, ty = opp_center
        best = None
        bestv = None
        for x, y in cand:
            if (x, y) in obstacles or not inb(x, y):
                continue
            d_to_opp = abs(x - tx) + abs(y - ty)
            d_from_self = abs(x - sx) + abs(y - sy)
            v = (d_from_self, d_to_opp)
            if best is None or v < bestv:
                best = (x, y)
                bestv = v
        target = best
    else:
        target = opp_center

    actions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    tx, ty = target

    best_move = [0, 0]
    best_score = None
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_cells:
            base = 0.0
        elif (nx, ny) in opp_cells:
            base = 1.5  # flipping into us
        else:
            base = 2.0   # likely unclaimed
        score = base
        score += -0.08 * (abs(nx - tx) + abs(ny - ty))  # approach target
        score += -0.03 * (abs(nx - ox) + abs(ny - oy))  # also pressure opponent area
        score += 0.001 * ((dx == 0 and dy == 0))         # slight preference to avoid oscillations
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move