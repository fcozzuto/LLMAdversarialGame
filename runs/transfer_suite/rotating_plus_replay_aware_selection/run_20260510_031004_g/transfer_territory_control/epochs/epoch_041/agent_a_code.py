def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_adj = max(abs(sx - px), abs(sy - py)) == 1

    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: claim unclaimed; re-enter self is safe; entering opponent flips.
        v = 0
        if (nx, ny) in unclaimed:
            v += 220
        if (nx, ny) in self_terr:
            v += 18
        if (nx, ny) in opp_terr:
            v += 110

        # Voronoi pressure: prefer being closer to that cell than the opponent.
        ds = abs(nx - sx) + abs(ny - sy)
        do = abs(nx - px) + abs(ny - py)
        v += (do - ds) * 6

        # Move toward opponent if it means immediate flip opportunity.
        if (nx, ny) in opp_terr and opp_adj:
            v += 40

        # Slight preference for reducing distance to nearest unclaimed if any.
        if unclaimed:
            ux, uy = min(unclaimed, key=lambda t: abs(t[0] - nx) + abs(t[1] - ny))
            v += max(0, 40 - (abs(ux - nx) + abs(uy - ny))) * 2

        # Deterministic tie-break: lexicographic on (dx,dy) after value.
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return best