def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_move = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Prefer closest resource, tie-break by move lexicographic and away from opponent a bit
            score = None
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = r[0], r[1]
                    if isinstance(rx, int) and isinstance(ry, int):
                        d = max(abs(rx - nx), abs(ry - ny))
                        if score is None or d < score:
                            score = d
            if score is None:
                score = 10**9
            opp = max(abs(ox - nx), abs(oy - ny))
            key = (score, -opp, dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: move toward center while keeping distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        to_center = max(abs(cx - nx), abs(cy - ny))
        from_opp = max(abs(ox - nx), abs(oy - ny))
        key = (to_center, -from_opp, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]