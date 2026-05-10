def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    opp_t = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    self_t = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if opp_t:
        ax = sum(x for x, _ in opp_t) / len(opp_t)
        ay = sum(y for _, y in opp_t) / len(opp_t)
    else:
        ax, ay = opp_pos[0], opp_pos[1]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        base = 0
        if (nx, ny) in opp_t:
            base += 3  # flip claim on entry
        elif (nx, ny) in un:
            base += 2
        elif (nx, ny) in self_t:
            base += 0
        else:
            base += 0

        # Shape toward center while keeping some pressure away from opponent centroid
        dcen = abs(nx - cx) + abs(ny - cy)
        dopp = abs(nx - ax) + abs(ny - ay)
        # Prefer reducing center distance and increasing opponent distance
        score = base + (-0.15 * dcen) + (0.06 * dopp)

        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]