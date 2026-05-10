def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    ti = int(observation.get("turn_index", 0) or 0)
    best = None
    bestv = None

    def clamp(x, y):
        if x < 0: x = 0
        if y < 0: y = 0
        if x >= w: x = w - 1
        if y >= h: y = h - 1
        return x, y

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)

        # Avoid moving "into" obstacles (or too close).
        pen_obs = 0
        if (nx, ny) in obs:
            pen_obs = 10**6
        else:
            for ax, ay in obs:
                d = abs(nx - ax) + abs(ny - ay)
                if d == 1:
                    pen_obs += 25
                elif d == 2:
                    pen_obs += 8

        man_to_opp = abs(nx - ox) + abs(ny - oy)
        wall = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        corner_bias = abs(nx - tx) + abs(ny - ty)

        if is_evader:
            # Maximize survival distance, prefer hugging a "good" corner but not crashing into walls.
            v = (man_to_opp * 10) + (corner_bias * 2) + (wall * (2 if ti % 2 == 0 else 1)) - pen_obs
        else:
            # Pursuer: minimize distance, with a small preference toward the farthest evasion corner for forcing zigzags.
            v = (-man_to_opp * 10) + (wall * 1) - pen_obs - (corner_bias * 0.5)

        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]