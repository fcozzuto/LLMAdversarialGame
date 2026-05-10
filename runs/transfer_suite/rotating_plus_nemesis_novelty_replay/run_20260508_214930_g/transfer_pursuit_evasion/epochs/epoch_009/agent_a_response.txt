def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    actions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    base = dist2(sx, sy)

    # Deterministic heuristic: maximize distance; avoid obstacles; prefer breaking out of obstacle adjacency.
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if blocked(nx, ny):
            nx, ny = sx, sy

        d = dist2(nx, ny)

        # obstacle adjacency penalty (more penalty if staying adjacent)
        adj = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                if blocked(nx + tx, ny + ty) if inb(nx + tx, ny + ty) else False:
                    adj += 1

        # keep from clustering with opponent: big bonus if strictly farther than base
        gain = d - base
        score = d + 5 * (1 if gain > 0 else 0) - 2 * adj - 0.5 * (1 if gain < 0 else 0)

        # deterministic tie-breaker: prefer action ordering already in list, via strict ">" only
        if best_score is None or score > best_score:
            best_score = score
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]