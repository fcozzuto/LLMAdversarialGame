def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    def score_pos(x, y):
        # Base pursuit/evasion on distance.
        d = abs(x - ox) + abs(y - oy)
        # Obstacle "risk": prefer squares with fewer blocked neighbors (deterministic).
        risk = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if blocked(nx, ny):
                    risk += 1
        # Corner bias to avoid dithering; evader goes to farthest corner, pursuer to nearest.
        cb = 0
        best_corner = corners[0]
        if is_evader:
            best_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            cb = (abs(x - best_corner[0]) + abs(y - best_corner[1]))  # larger is better for evader
        else:
            best_corner = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
            cb = (-(abs(x - best_corner[0]) + abs(y - best_corner[1])))  # closer is better for pursuer
        # Combine: pursuer maximizes negative distance, evader maximizes positive distance.
        if is_evader:
            return d * 10 - risk * 2 + cb
        else:
            return (-d) * 10 - risk * 2 + cb

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v = score_pos(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best = (dx, dy)
    if best is None:
        # All moves blocked: deterministic stay.
        return [0, 0]
    return [best[0], best[1]]