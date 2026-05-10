def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, S):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            ax, ay = nx + dx, ny + dy
            if (ax, ay) in S:
                c += 1
        return c

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        score = -0.2  # slight cost to reduce dithering
        if (nx, ny) in oppT:
            score += 28.0 + 2.0 * adj_count(nx, ny, selfT) - 1.0 * adj_count(nx, ny, oppT)
        elif (nx, ny) in selfT:
            score -= 1.0 + 0.5 * adj_count(nx, ny, oppT)
        elif (nx, ny) in unclaimed:
            score += 10.0 + 0.7 * adj_count(nx, ny, selfT) - 0.4 * adj_count(nx, ny, oppT)
        else:
            score += 3.0 + 0.5 * adj_count(nx, ny, selfT) - 0.2 * adj_count(nx, ny, oppT)
        if (nx, ny) == tuple(observation.get("opponent_position")):
            score -= 5.0
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    if best[0] is not None and best[1] > 0:
        return [best[0][0], best[0][1]]

    # Fallback: move deterministically toward nearest unclaimed or opponent cell
    targets = list(unclaimed) if unclaimed else (list(oppT) if oppT else [])
    if not targets:
        return [0, 0]
    tx, ty = min(targets, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[1], p[0]))
    dx = 0 if tx == x else (1 if tx > x else -1)
    dy = 0 if ty == y else (1 if ty > y else -1)

    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for cdx, cdy in cand:
        nx, ny = x + cdx, y + cdy
        if inb(nx, ny):
            return [cdx, cdy]
    return [0, 0]