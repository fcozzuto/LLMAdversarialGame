def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            selfT.add((p[0], p[1]))

    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            oppT.add((p[0], p[1]))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((p[0], p[1]))

    if unclaimed:
        # Keep only a small deterministic subset for speed
        unclaimed_sorted = sorted(unclaimed, key=lambda c: (abs(c[0]-sx)+abs(c[1]-sy), c[0], c[1]))
        unclaimed_use = unclaimed_sorted[:12]
    else:
        unclaimed_use = []

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None
    best_key = None

    def md(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        gain = 0
        if cell in oppT:
            gain += 6
        elif cell in unclaimed:
            gain += 3
        elif cell in selfT:
            gain += 1

        if unclaimed_use:
            dmin = 10**9
            for c in unclaimed_use:
                dmin = min(dmin, abs(c[0]-nx) + abs(c[1]-ny))
            gain += 2.0 / (1 + dmin)
        # Small bias to advance toward opponent (territory sweeper)
        gain += -0.05 * (abs(nx-ox) + abs(ny-oy))

        key = (-gain, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]