def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def parse_cells(key):
        out = []
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                out.append((int(p[0]), int(p[1])))
        return out

    unclaimed = parse_cells("unclaimed_cells")
    opp_terr = set(parse_cells("opponent_territory"))
    self_terr = set(parse_cells("self_territory"))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18

    # Precompute target: nearest unclaimed if any
    target = None
    if unclaimed:
        bestd = 10**18
        for cx, cy in unclaimed:
            if 0 <= cx < w and 0 <= cy < h:
                d = abs(cx - x) + abs(cy - y)
                if d < bestd:
                    bestd = d
                    target = (cx, cy)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        sc = 0
        if target:
            sc += - (abs(target[0] - nx) + abs(target[1] - ny))
        else:
            sc += (abs(nx - ox) + abs(ny - oy))  # safer default

        if (nx, ny) in opp_terr:
            sc += 3
        if (nx, ny) in self_terr:
            sc -= 1
        # slight preference to avoid being adjacent to opponent
        sc += -max(0, 2 - (abs(nx - ox) + abs(ny - oy)))

        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]