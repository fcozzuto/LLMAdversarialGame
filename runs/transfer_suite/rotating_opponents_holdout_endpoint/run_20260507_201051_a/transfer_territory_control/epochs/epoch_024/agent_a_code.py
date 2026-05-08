def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs8 = moves

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_op(x, y):
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in ot:
                return True
        return False

    # Choose a deterministic frontier target: unclaimed adjacent to opponent territory, else any unclaimed, else opponent cells, else stay.
    frontier = []
    for x, y in unclaimed:
        if adj_to_op(x, y):
            frontier.append((x, y))
    candidates = frontier if frontier else list(unclaimed) if unclaimed else (list(ot) if ot else [])
    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def target_cost(p):
        x, y = p
        d = abs(x - sx) + abs(y - sy)
        center_bias = abs(x - cx) + abs(y - cy)
        # Prefer nearer to us, and slightly toward center.
        return (d, center_bias, x, y)

    tx, ty = sorted(candidates, key=target_cost)[0]

    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = 0
        if (nx, ny) in st:
            score += 2
        if (nx, ny) in ot:
            score += 6  # stepping into opponent territory is profitable due to flipping-on-entry
        if (nx, ny) in unclaimed:
            score += 4
        # Move closer to target
        dist = abs(tx - nx) + abs(ty - ny)
        score += 3 * (-dist)
        # Avoid stepping into opponent territory unless it improves distance to target
        if (nx, ny) in ot:
            score += 1 if dist <= abs(tx - sx) + abs(ty - sy) else -1
        # Mildly avoid edges early by preferring toward center
        score += -0.05 * (abs(nx - cx) + abs(ny - cy))
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        return [0, 0]
    return [int(best[1]), int(best[2])]