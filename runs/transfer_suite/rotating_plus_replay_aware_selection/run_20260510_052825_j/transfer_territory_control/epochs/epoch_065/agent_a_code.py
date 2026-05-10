def choose_move(observation):
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (None, None))

    obstacles = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = set((p[0], p[1]) for p in unclaimed if p is not None and len(p) >= 2)

    selfT = observation.get("self_territory") or []
    selfT = set((p[0], p[1]) for p in selfT if p is not None and len(p) >= 2)

    oppT = observation.get("opponent_territory") or []
    oppT = set((p[0], p[1]) for p in oppT if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not unclaimed and not oppT:
        return [0, 0]

    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 10
        elif (nx, ny) in oppT:
            score += 3
        elif (nx, ny) in selfT:
            score += 1

        if ox is not None and oy is not None:
            d = abs(nx - ox) + abs(ny - oy)
            score += 0.02 * d  # deterministic preference to stay away

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]