def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = -10**18
        for i, (rx, ry) in enumerate(resources):
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)

            # If we can reach it no later than opponent, strongly prefer.
            # Otherwise still prefer to "deny" by moving toward what opponent is closest to.
            if (sd == 0 and nx == rx and ny == ry):
                s = 10**9
            else:
                s = (od - sd) * 220 - sd * 3

            # Mild tie-break: earlier index (deterministic) and avoid too-far targets.
            s -= i * 0.001

            # Prefer resources roughly in our direction (reduces dithering).
            vx = rx - nx; vy = ry - ny
            if vx == 0 and vy == 0:
                dir_bonus = 0
            else:
                if abs(vx) >= abs(vy):
                    dir_bonus = 8 if (vx > 0) == (dx > 0) else (-8 if dx < 0 else 0)
                else:
                    dir_bonus = 8 if (vy > 0) == (dy > 0) else (-8 if dy < 0 else 0)
            s += dir_bonus

            if s > move_score:
                move_score = s

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move