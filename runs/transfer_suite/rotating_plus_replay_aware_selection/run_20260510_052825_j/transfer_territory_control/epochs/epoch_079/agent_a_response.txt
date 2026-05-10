def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    selfT = set(map(tuple, observation.get("self_territory") or []))
    oppT = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    # Heuristic frontier targets: unclaimed near our territory, else near opponent
    frontier_targets = []
    if selfT:
        for (tx, ty) in unclaimed:
            if abs(tx - sx) + abs(ty - sy) > w + h:
                continue
            # prefer cells near our claimed cells (small boundary distance)
            best = 10**9
            for (px, py) in selfT:
                d = abs(tx - px) + abs(ty - py)
                if d < best:
                    best = d
            if best <= 3:
                frontier_targets.append((tx, ty, best))
        frontier_targets.sort(key=lambda t: (t[2], abs(t[0] - sx) + abs(t[1] - sy)))
    if not frontier_targets:
        # fall back: prioritize expanding around where opponent currently is
        for (tx, ty) in unclaimed:
            frontier_targets.append((tx, ty, abs(tx - ox) + abs(ty - oy)))
        frontier_targets.sort(key=lambda t: (t[2], abs(t[0] - sx) + abs(t[1] - sy)))

    target = frontier_targets[0][:2] if frontier_targets else (ox, oy)
    tx, ty = target

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (-10**18, 0, 0)

    # Encourage capturing: unclaimed big, opponent smaller but plus if it reduces distance to our target
    # Also discourage stepping into obstacle (engine will keep position anyway; we avoid to be safe).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        gain = 0.0
        if (nx, ny) in unclaimed:
            gain += 10.0
        if (nx, ny) in oppT:
            gain += 6.0
        if (nx, ny) in selfT:
            gain += 1.0

        # Move toward a frontier target
        d_now = abs(sx - tx) + abs(sy - ty)
        d_new = abs(nx - tx) + abs(ny - ty)
        gain += (d_now - d_new) * 1.5

        # Prefer perimeter/edge expansion slightly (avoid getting trapped near center)
        gain += (w + h - 2 * edge_dist(nx, ny)) * 0.03

        # If opponent is close, slightly prioritize counterclaiming their territory
        d_opp = abs(nx - ox) + abs(ny - oy)
        gain += (5 - min(5, d_opp)) * (2.0 if (nx, ny) in oppT else 0.6)

        if gain > best[0]:
            best = (gain, dx, dy)

    if best[0] <= -10**17:
        return [0, 0]
    return [int(best[1]), int(best[2])]