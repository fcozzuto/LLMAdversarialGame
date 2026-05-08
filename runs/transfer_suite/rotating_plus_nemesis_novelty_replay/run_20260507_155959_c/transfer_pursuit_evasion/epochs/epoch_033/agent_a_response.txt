def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in cand:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                m += 1
        return m

    best = None
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        md = abs(ox - nx) + abs(oy - ny)
        cd = abs(ox - nx) if abs(ox - nx) > abs(oy - ny) else abs(oy - ny)
        diag = abs(dx) + abs(dy)  # prefer diagonal/active pursuit
        key = (md, cd, -diag, -mobility(nx, ny), -nx, -ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]