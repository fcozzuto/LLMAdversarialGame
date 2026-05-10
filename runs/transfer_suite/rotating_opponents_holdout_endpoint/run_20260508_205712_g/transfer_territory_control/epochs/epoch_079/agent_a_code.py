def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for k in ("unclaimed_cells", "resources"):
        for p in (observation.get(k) or []):
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))

    if not targets:
        for k in ("self_territory", "opponent_territory"):
            for p in (observation.get(k) or []):
                if p and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                        targets.append((x, y))
        if not targets:
            targets = [(ox, oy)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_score = None

    # Prefer moves that get closer to the closest target, but avoid moving into obstacles/bounds.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_to_target = min(manh((nx, ny), t) for t in targets) if targets else manh((nx, ny), (ox, oy))
        d_to_opp = manh((nx, ny), (ox, oy))
        score = (-(d_to_target), d_to_opp, -dx, -dy)  # deterministic tie-breaks
        if best is None or score > best_score:
            best_score, best = score, [dx, dy]

    if best is not None:
        return best

    # Fallback: stay or move deterministically to any safe adjacent cell.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]