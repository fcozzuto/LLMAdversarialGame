def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "flee"))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or x < 0 or x >= w or y < 0 or y >= h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def adj_blocked_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    c += 1
        return c

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        trap = adj_blocked_count(nx, ny)

        # Heuristic:
        # - Evader: maximize distance, minimize trap-ness.
        # - Pursuer: minimize distance, minimize being trapped (avoid corners/holes).
        if is_evader:
            score = d * 10 - trap * 2
        else:
            score = (-d) * 10 - trap * 1

        # Tiny deterministic bias toward staying closer to board center when equal
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = - (abs(nx - cx) + abs(ny - cy)) * 0.01
        score += center_bias

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]