def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed if 0 <= int(x) < w and 0 <= int(y) < h and (int(x), int(y)) not in obstacles]

    # Build frontier targets near our current territory to expand locally; fall back to unclaimed/edges.
    my_terr = observation.get("self_territory") or []
    my_set = {(int(x), int(y)) for x, y in my_terr if 0 <= int(x) < w and 0 <= int(y) < h}
    frontier = set()
    if my_set:
        for (x, y) in my_set:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in my_set:
                    frontier.add((nx, ny))
    candidates = []
    if unclaimed:
        # Prefer unclaimed far from opponent (safe expansion) but not too far from us.
        for x, y in unclaimed:
            candidates.append((x, y))
    if frontier:
        # Frontier often yields fast territory gains.
        candidates += list(frontier)
    if not candidates:
        # Edge fallback.
        candidates = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
        candidates = [(x, y) for (x, y) in candidates if (x, y) not in obstacles and inb(x, y)]

    # Select a deterministic target: maximize separation from opponent, minimize distance from us.
    best_t = None
    best_key = None
    for x, y in candidates:
        sep = dist2(x, y, ox, oy)
        near = dist2(x, y, sx, sy)
        # Prefer unclaimed slightly stronger (if present), otherwise frontier/edges still work.
        is_unclaimed = 1 if (x, y) in set(unclaimed) else 0
        key = (sep, is_unclaimed, -near, -(abs(x - (w - 1) / 2) + abs(y - (h - 1) / 2)))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t if best_t is not None else (sx, sy)

    # Move greedily toward target while also discouraging getting too close to opponent.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: approach target.
        score = -dist2(nx, ny, tx, ty)
        # Secondary: keep distance from opponent to avoid being flipped/swarmed.
        score += 0.15 * dist2(nx, ny, ox, oy)
        # Small preference for expanding into unclaimed cells if adjacent.
        if unclaimed and (nx, ny) in set(unclaimed):
            score += 2.0
        # Slight tie-break: prefer progressing in our general direction (diagonal if useful).
        score += -0.01 * (abs(nx - sx) + abs(ny - sy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move