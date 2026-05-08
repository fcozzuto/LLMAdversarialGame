def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    selfT = set(tuple(p) for p in observation.get("self_territory", []))
    oppT = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                pass
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs_to_unclaimed = []
    for (x, y) in unclaimed:
        d = man((sx, sy), (x, y))
        if d <= 6:
            dirs_to_unclaimed.append((d, x, y))
    dirs_to_opp = []
    for (x, y) in oppT:
        d = man((sx, sy), (x, y))
        if d <= 6:
            dirs_to_opp.append((d, x, y))
    dirs_to_unclaimed.sort()
    dirs_to_opp.sort()

    # Prefer immediate gain; else move toward nearest meaningful target.
    target_unclaimed = (dirs_to_unclaimed[0][1], dirs_to_unclaimed[0][2]) if dirs_to_unclaimed else None
    target_opp = (dirs_to_opp[0][1], dirs_to_opp[0][2]) if dirs_to_opp else None

    best = None
    for dx, dy, nx, ny in moves:
        cell = (nx, ny)
        score = 0

        # Immediate territory gain on entry (flipping enabled).
        if cell in unclaimed:
            score += 50
        elif cell in oppT:
            score += 80
        elif cell in selfT:
            score += 5

        # Avoid getting too close to opponent if we're not making progress.
        dist_o = man((nx, ny), (ox, oy))
        score -= max(0, 6 - dist_o) * 2

        if target_unclaimed is not None:
            score -= man((nx, ny), target_unclaimed) * 1
        if target_opp is not None:
            # Strongly attract toward opponent territory if available.
            score -= man((nx, ny), target_opp) * 2

        # Slight preference for moving away from obstacles isn't needed since we filter them.
        # Deterministic tie-break using lexicographic move.
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1]