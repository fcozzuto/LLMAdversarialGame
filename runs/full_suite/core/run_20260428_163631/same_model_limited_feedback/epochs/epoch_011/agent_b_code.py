def choose_move(observation):
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", [])
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer cells that reduce opponent score pressure:
        # 1) move closer to a "winning" resource (opponent farther than us),
        # 2) else reduce distance to opponent.
        score = -md(nx, ny, ox, oy)
        for r in resources:
            if not isinstance(r, (list, tuple)) or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            score += 3 * adv - 0.1 * sd

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]