def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    # Evader tries to run to the corner farthest from pursuer; pursuer goes straight at opponent.
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = dist2(nx, ny, tx, ty)
        # Small tie-breaker toward staying away from obstacles: penalize being adjacent to obstacles.
        adj_obs = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                adj_obs += 1

        if is_evader:
            val = (d_opp * 5.0) + (d_tgt * 0.02) - (adj_obs * 0.5)
            better = (best_val is None) or (val > best_val)
        else:
            val = (-d_opp * 5.0) + (-d_tgt * 0.02) - (adj_obs * 0.5)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    return best_move