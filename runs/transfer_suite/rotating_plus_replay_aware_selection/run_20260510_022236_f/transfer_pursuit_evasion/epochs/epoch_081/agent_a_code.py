def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return (x, y) in obstacles or not (0 <= x < w and 0 <= y < h)

    def blocked_neighbors(x, y):
        nb = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if blocked(x + dx, y + dy):
                    nb += 1
        return nb

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        trap = blocked_neighbors(nx, ny)  # 0..8
        # Deterministic tie-break order: iteration order in moves.
        if is_evader:
            # Run away, avoid being near "dead ends"/corners.
            score = dist + (8 - trap) * 0.35
        else:
            # Chase while avoiding moves that trap us.
            score = (-dist) + (8 - trap) * 0.08
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]