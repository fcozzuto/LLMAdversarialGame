def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    selft = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny):
                        yield nx, ny

    # Pick a deterministic target unclaimed cell: closest to our territory (or our position).
    target = None
    best = 10**9
    if unclaimed:
        base = selft if selft else {(sx, sy)}
        for ux, uy in sorted(unclaimed):
            d = min(abs(ux - bx) + abs(uy - by) for bx, by in base)
            if d < best:
                best = d
                target = (ux, uy)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = 0
            if (nx, ny) in unclaimed:
                score += 10
            # Bonus if move expands near our territory.
            if any((px, py) in selft for px, py in neigh8(nx, ny)):
                score += 3
            # Goal direction: closer to target unclaimed (if any), otherwise toward unclaimed.
            if target:
                score += - (abs(target[0] - nx) + abs(target[1] - ny))
            else:
                score += - (abs(ox - nx) + abs(oy - ny))
            # Deterministic tie-break.
            candidates.append((-(score), dx, dy))
    if candidates:
        candidates.sort()
        return [candidates[0][1], candidates[0][2]]
    return [0, 0]