def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    resources = set(tuple(p) for p in (observation.get("resources", []) or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Center bias helps against center-claim archetype
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (0, 0)
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0.0
        # Prefer staying/expanding our territory
        if (nx, ny) in self_terr:
            v += 30
        if (nx, ny) in unclaimed:
            v += 12
        # If flipping opponent territory is possible/valuable, prioritize it more
        if (nx, ny) in opp_terr:
            v += 40

        # Distance pressure: get closer to opponent without suicidal aim
        d_opp = abs(nx - ox) + abs(ny - oy)
        v += (20 - 3.0 * d_opp)

        # Center control bias
        v += 6.0 * (-(abs(nx - cx) + abs(ny - cy)))

        # Resource attraction (if any)
        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            v += max(0, 60 - 4.0 * d_res)

        # Mild preference to reduce local risk: move toward cells not currently opponent-owned
        if (nx, ny) in opp_terr:
            v -= 1.5 * abs(sx - nx) + 1.5 * abs(sy - ny)

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]