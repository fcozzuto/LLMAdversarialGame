def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (7, 7))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_d(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for ux, uy in unclaimed:
        if (ux, uy) in obstacles:
            continue
        targets.append((edge_d(ux, uy), (ux, uy)))
    targets.sort(key=lambda t: (-t[0], dist((sx, sy), t[1])))
    target = targets[0][1] if targets else None

    best = (0, 0, -10**18)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = 0.0
            if (nx, ny) in unclaimed:
                score += 10.0 + 0.7 * edge_d(nx, ny)
            elif (nx, ny) in oppT:
                score += 12.0 + 0.5 * edge_d(nx, ny)
            elif (nx, ny) in selfT:
                score += 1.0
            else:
                score += 0.5 * edge_d(nx, ny)

            # Push into interior; avoid being lured to opponent edge claims
            if target is not None:
                score += 0.35 * (-dist((nx, ny), target))
            # Contain: prefer cells that reduce distance to our territory boundary vs opponent
            d1 = dist((nx, ny), (ox, oy))
            score += -0.03 * d1

            # Prefer safer continued expansion (not forced back into corners)
            score += 0.02 * edge_d(nx, ny)

            if score > best[2] or (score == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, score)

    dx, dy, _ = best
    return [int(dx), int(dy)]