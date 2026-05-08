def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x0, y0 = observation.get("self_position", [0, 0]) or [0, 0]
    xo, yo = observation.get("opponent_position", [0, 0]) or [0, 0]
    x0, y0, xo, yo = int(x0), int(y0), int(xo), int(yo)

    obstacles = observation.get("obstacles", []) or []
    ox = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            try:
                ox.add((int(p[0]), int(p[1])))
            except:
                pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny) or (nx, ny) in ox:
            continue
        # Deterministic heuristic: approach opponent
        dist = max(abs(nx - xo), abs(ny - yo))
        # Tie-breaker: prefer smaller dx then dy then staying
        tieb = (abs(dx), abs(dy), 0 if dx == 0 and dy == 0 else 1)
        val = (dist, tieb, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # No legal moves: deterministically stay put
    return [0, 0]