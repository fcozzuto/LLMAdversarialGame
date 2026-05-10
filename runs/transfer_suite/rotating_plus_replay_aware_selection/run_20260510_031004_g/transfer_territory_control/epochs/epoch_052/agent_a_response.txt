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

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = 0

        # Territory capture incentives
        if (nx, ny) in unclaimed:
            v += 320
        if (nx, ny) in self_terr:
            v += 15
        if (nx, ny) in opp_terr:
            v += 95  # flipping on entry

        # Pressure: move toward nearest unclaimed, but also toward opponent-owned near our frontier
        if unclaimed:
            dmin = min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed)
            v += 80 - 2 * dmin
        else:
            v += 0

        # If stepping adjacent to opponent, increase contest value (edge-claim archetype)
        if max(abs(nx - px), abs(ny - py)) == 1:
            v += 60

        # Mildly avoid getting too close without gaining ground
        v += 2 * (abs(nx - px) + abs(ny - py)) * -0.2  # keep deterministic small effect

        # Prefer not to backtrack into already controlled area unless it's useful
        if (nx, ny) in self_terr and (nx, ny) not in unclaimed:
            v -= 5

        candidates.append((v, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]