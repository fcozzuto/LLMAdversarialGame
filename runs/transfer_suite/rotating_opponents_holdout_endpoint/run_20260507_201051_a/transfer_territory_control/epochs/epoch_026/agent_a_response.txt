def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Build a small set of meaningful targets near the border with opponent territory.
    frontier = []
    for (x, y) in unclaimed:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if (x + dx, y + dy) in ot:
                frontier.append((x, y))
                break
    if not frontier:
        frontier = list(unclaimed)[:64] if unclaimed else []
    if not frontier:
        frontier = list(ot)[:64] if ot else []

    # If we have a reasonable frontier, bias toward the nearest; otherwise use center pressure.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if frontier:
        tx, ty = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy), p[0], p[1]))
    else:
        tx, ty = (cx, cy)

    def score_cell(x, y):
        if not in_bounds(x, y):
            return -10**9
        base = 0
        if (x, y) in unclaimed:
            base += 30
        if (x, y) in ot:
            base += 22
        if (x, y) in st:
            base += 6
        # Prefer moving closer to target and also toward center slightly.
        base += -(abs(x - tx) + abs(y - ty))
        base += -0.25 * (abs(x - cx) + abs(y - cy))
        # Mild repulsion from obstacles adjacency (deterministic).
        adj_obs = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                adj_obs += 1
        base -= 0.8 * adj_obs
        return base

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        # Deterministic tie-break: prefer staying still? no: prefer lower dx, then lower dy.
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]