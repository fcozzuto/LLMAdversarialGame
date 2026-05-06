def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_move = (0, 0, -10**9, 10**9)
    for dx, dy, nx, ny in legal:
        if resources:
            best = -10**9
            tie = 10**9
            for rx, ry in resources:
                sd = d_cheb(nx, ny, rx, ry)
                od = d_cheb(ox, oy, rx, ry)
                # Prefer resources where we gain distance over opponent (contested advantage).
                val = (od - sd) * 12 - sd
                if val > best or (val == best and (sd < tie or (sd == tie and (rx + ry) < (tie + 0)))):
                    best = val
                    tie = sd
            # Small center bias to stabilize when contest is similar.
            val2 = best - d_cheb(nx, ny, cx, cy) * 0.5
            key2 = tie
        else:
            sd = d_cheb(nx, ny, cx, cy)
            val2 = -sd
            key2 = sd
        if val2 > best_move[2] or (val2 == best_move[2] and key2 < best_move[3]):
            best_move = (dx, dy, val2, key2)

    return [int(best_move[0]), int(best_move[1])]