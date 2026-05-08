def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("evade" in self_role)
    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2): 
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    parity = int(observation.get("turn_index", 0) or 0) & 1

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dC = cheb(nx, ny, ox, oy)
        dM = abs(nx - ox) + abs(ny - oy)

        # Zigzag interceptor bias: alternate prioritizing closing x vs y.
        bias = (abs(nx - ox) if parity == 0 else abs(ny - oy))
        # Small obstacle "nearby" penalty (robustness without scanning too much).
        near_obs = 0
        for ax, ay in ((nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)):
            if (ax, ay) in obstacles:
                near_obs += 1

        # If evader: maximize distance; else minimize.
        if is_evader:
            val = -(dC * 10.0 + dM * 1.0) + bias * 0.05 + near_obs * 2.0
        else:
            val = (dC * 10.0 + dM * 1.0) + bias * 0.05 + near_obs * 2.0

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move