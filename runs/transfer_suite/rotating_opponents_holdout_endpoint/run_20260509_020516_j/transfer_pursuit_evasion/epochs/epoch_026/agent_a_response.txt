def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_points(key):
        pts = []
        for it in observation.get(key, []) or []:
            if it is None:
                continue
            if isinstance(it, dict):
                x = it.get("x", it.get(0, None))
                y = it.get("y", it.get(1, None))
            else:
                x, y = it[0], it[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                pts.append((x, y))
        return pts

    obstacles = set(parse_points("obstacles"))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manhattan(a, b, c, d):
        return abs(a - c) + abs(b - d)

    obs_list = list(obstacles)

    best = None
    best_key = None
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = manhattan(nx, ny, ox, oy)
        # If multiple candidates tie on distance, prefer those that keep away from obstacles.
        if obs_list:
            mind = min(abs(nx - ex) + abs(ny - ey) for ex, ey in obs_list)
        else:
            mind = 10
        # Tie-break deterministically using turn parity and candidate index.
        parity = (int(observation.get("turn_index", 0) or 0) + i) & 1
        # Primary: minimize distance; Secondary: maximize obstacle clearance; Tertiary: deterministic.
        key = (dist, -mind, parity, i)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]