def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    evading = ("evad" in self_role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist(x, y):
        return abs(x - ox) + abs(y - oy)

    def adj_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    ti = int(observation.get("turn_index", 0) or 0)
    # Prefer breaking symmetry: rotate move order deterministically with turn index.
    k = ti % len(moves)
    moves = moves[k:] + moves[:k]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # deterministic "engine keeps in place"
        dist = mindist(nx, ny)
        ao = adj_obs(nx, ny)
        # If chasing: minimize distance, avoid obstacles; if evading: maximize distance, avoid corners.
        val = (-dist if evading else dist) - (0.75 * ao) + (0.02 * (nx + ny))
        if best is None or (val > best_val if evading else val < best_val):
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            # tie-break deterministically by move order
            if moves.index((dx, dy)) < moves.index(best):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]