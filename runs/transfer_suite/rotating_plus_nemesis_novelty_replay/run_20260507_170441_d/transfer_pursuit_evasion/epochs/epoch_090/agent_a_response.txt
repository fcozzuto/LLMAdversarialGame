def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x = y = None
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
        elif isinstance(o, dict):
            if "x" in o and "y" in o:
                x, y = int(o["x"]), int(o["y"])
        if x is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # If we can capture (pursuer): move directly onto opponent if legal
    if not is_evader and free(ox, oy):
        dx, dy = ox - sx, oy - sy
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]

    best = None
    best_val = None
    # Deterministic tie-breaking by move order.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist = d2(nx, ny, ox, oy)
        val = dist if is_evader else -dist
        if best is None or val > best_val:
            best, best_val = (dx, dy), val
    return [best[0], best[1]]