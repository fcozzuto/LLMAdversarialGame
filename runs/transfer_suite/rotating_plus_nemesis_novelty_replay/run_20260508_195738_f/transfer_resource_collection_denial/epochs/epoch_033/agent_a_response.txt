def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: md(ox, oy, c[0], c[1]) - 0.01 * md(sx, sy, c[0], c[1]))
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    # Prefer: move that gives us a contest win next step; otherwise minimize being behind.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        val = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # Contest outcome: if we're <= opponent, strong preference.
            # Tie-break: prefer closer.
            win_margin = do - ds  # positive if we're faster
            score = 1000 * (1 if win_margin >= 0 else 0) + 50 * win_margin - ds
            # Encourage going to closer resources even when we're slightly behind.
            if val is None or score > val:
                val = score
        if val is None:
            continue
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]