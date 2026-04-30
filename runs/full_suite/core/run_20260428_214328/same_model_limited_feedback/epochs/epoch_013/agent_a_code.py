def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            v = dist2(nx, ny, ox, oy)
            if best is None or v > bestv or (v == bestv and (abs(dx) + abs(dy) < best)):
                best, bestv = dx + 10 * dy, v
        dx, dy = bestv = None, None
        # deterministic fallback
        for dx, dy, nx, ny in moves:
            if dist2(nx, ny, ox, oy) == max(dist2(mx, my, ox, oy) for _, _, mx, my in moves):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0, sx, sy)
    best_val = None
    best_res_dist = None
    for dx, dy, nx, ny in moves:
        # Relative advantage picking: prefer resources where opponent is far relative to us from next position
        local_best = None
        local_dist = None
        for rx, ry in resources:
            oppd = dist2(ox, oy, rx, ry)
            sd = dist2(nx, ny, rx, ry)
            v = oppd - sd
            if local_best is None or v > local_best or (v == local_best and sd < local_dist):
                local_best, local_dist = v, sd
        # Also avoid getting too close to opponent unless it helps
        safety = dist2(nx, ny, ox, oy)
        val = (local_best, safety)
        if best_val is None or val > best_val or (val == best_val and local_dist < best_res_dist):
            best_val = val
            best_res_dist = local_dist
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]