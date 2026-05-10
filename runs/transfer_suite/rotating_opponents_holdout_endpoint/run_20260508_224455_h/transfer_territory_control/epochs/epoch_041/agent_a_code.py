def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for c in observation.get("obstacles", []) or []:
        obstacles.add((int(c[0]), int(c[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (None, -10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        gain = 0
        if (nx, ny) in self_terr:
            gain += 1
        elif (nx, ny) in unclaimed:
            gain += 3
        elif (nx, ny) in opp_terr:
            gain += 4  # flipping on entry

        # Prefer approaching center and opponent, but prioritize actual control gains
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        block = 0
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)):
            if inb(ax, ay) and (ax, ay) in obstacles:
                block += 0.2

        # Frontier bias: slightly prefer moving adjacent to our territory if unclaimed/opponent there
        frontier = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in self_terr:
                    frontier = 0.6
                    break
            if frontier:
                break

        # Deterministic tie-break favors smaller dx, then smaller dy
        key = (gain * 10) - 0.3 * dist_center - 0.05 * dist_opp - block + frontier
        tie = (0 if gain >= 3 else 1, dx, dy)
        score = key - (tie[0] * 0.0001)

        if score > best[1]:
            best = ((dx, dy), score)
        elif score == best[1] and best[0] is not None:
            if (dx, dy) < best[0]:
                best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]