def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    selfT = to_set("self_territory")
    oppT = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Select a meaningful target: nearest unclaimed, otherwise nearest boundary cell not in obstacles.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        candidates = [(x, y) for x in range(w) for y in range(h)
                      if (x == 0 or y == 0 or x == w - 1 or y == h - 1) and (x, y) not in obstacles]
        if candidates:
            tx, ty = min(candidates, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        else:
            tx, ty = (w // 2, h // 2)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        d_to_target = abs(nx - tx) + abs(ny - ty)

        if (nx, ny) in oppT:
            score += 2000  # direct flip gain
        if (nx, ny) in unclaimed:
            score += 600  # expansion
        if (nx, ny) in selfT:
            score += 50   # consolidating

        # Encourage moving closer to the chosen target.
        score += max(0, 120 - 10 * d_to_target)

        # If we can flip, prefer it even more when adjacent to opponent territory already.
        if (nx, ny) in oppT or any((nx + ax, ny + ay) in oppT for ax in (-1, 0, 1) for ay in (-1, 0, 1) if (ax, ay) != (0, 0)):
            score += 150

        # Slightly discourage stepping into cells with heavy obstacle nearby (keep paths safe).
        neigh_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                axx, ayy = nx + ax, ny + ay
                if in_bounds(axx, ayy) and (axx, ayy) in obstacles:
                    neigh_obs += 1
        score -= 8 * neigh_obs

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]