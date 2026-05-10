def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in self_role) or ("evader" not in self_role)

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
        if is_pursuer:
            # Primary: minimize distance to opponent.
            # Tie-breakers: prefer moving toward opponent direction; avoid getting "stuck" near walls.
            step_toward = (1 if (dx != 0 and ((ox - sx) > 0) == (dx > 0)) or (dx == 0) else 0) + (
                1 if (dy != 0 and ((oy - sy) > 0) == (dy > 0)) or (dy == 0) else 0
            )
            wall_harm = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            score = (dist, -step_toward, wall_harm)
        else:
            # Evader: maximize distance, then move toward a more "cornered" escape relative to opponent.
            step_away = (1 if (dx != 0 and ((ox - sx) > 0) != (dx > 0)) else 0) + (
                1 if (dy != 0 and ((oy - sy) > 0) != (dy > 0)) else 0
            )
            corneriness = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)  # smaller => closer to corner
            score = (-dist, -step_away, corneriness)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]