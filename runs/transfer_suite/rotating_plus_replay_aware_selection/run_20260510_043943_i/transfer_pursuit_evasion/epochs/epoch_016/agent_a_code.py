def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if sx == 0 or sx == w - 1:
        pass
    dirs = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            dirs.append((dx, dy))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    sign = 1 if self_role == "evader" else -1
    best = None
    best_score = None

    # Small deterministic bias to prefer diagonal progress and away-from-potential-blocks.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        # Preferred direction: align move with coordinate delta to/from opponent.
        vx = ox - sx
        vy = oy - sy
        align = 0
        if vx != 0:
            align += 1 if (dx * vx) > 0 else (-1 if (dx * vx) < 0 else 0)
        if vy != 0:
            align += 1 if (dy * vy) > 0 else (-1 if (dy * vy) < 0 else 0)
        diag_bonus = 1 if dx != 0 and dy != 0 else 0

        # Obstacle proximity penalty encourages maneuvering around blocked tiles.
        obs_pen = 0
        for (px, py) in obstacles:
            dd = abs(nx - px) + abs(ny - py)
            if dd == 0:
                obs_pen += 100000
            elif dd == 1:
                obs_pen += 9
            elif dd == 2:
                obs_pen += 3

        # For pursuer: want lower d; for evader: want higher d.
        score = sign * d + 0.6 * align + 0.25 * diag_bonus - 0.15 * obs_pen

        if best_score is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]