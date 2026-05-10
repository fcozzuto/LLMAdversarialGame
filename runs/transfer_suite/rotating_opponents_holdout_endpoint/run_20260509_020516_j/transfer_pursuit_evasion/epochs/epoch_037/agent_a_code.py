def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if inside(x, y):
            obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    if not (is_pursuer or is_evader):
        is_pursuer = True

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def boundary_pen(x, y):
        # Smaller is better for pursuer; larger penalty for evader (to avoid being trapped by boundary)
        p = 0
        if x == 0 or x == w - 1:
            p += 3
        if y == 0 or y == h - 1:
            p += 3
        return p

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        dist_score = d2(nx, ny)
        if is_pursuer:
            # Prefer smaller distance; also avoid boundary a bit to keep escape routes if roles flip
            val = dist_score + boundary_pen(nx, ny) * 0.1
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Prefer larger distance; avoid going into immediate boundary walls
            val = dist_score - boundary_pen(nx, ny) * 0.6
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]