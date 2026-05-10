def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = abs(x - cx)
        dy = abs(y - cy)
        return (dx if dx > dy else dy)

    best_move = [0, 0]
    best_score = None

    # Deterministic tie-break: scan moves in fixed order above.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # If evader: don't step onto opponent's exact tile (capture radius 0, avoid contact).
        if (not is_pursuer) and nx == ox and ny == oy:
            continue

        dist = cheb(nx, ny, ox, oy)

        # Score: pursuer minimize distance; evader maximize distance; small tie-break to prefer center.
        c = center_bias(nx, ny)
        if is_pursuer:
            score = (-dist, c)  # higher tuple is better; make distance negative
        else:
            score = (dist, -c)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move