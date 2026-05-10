def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_move = [0, 0]
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            best_here = -10**9
            for rx, ry in resources:
                rx = int(rx)
                ry = int(ry)
                d1 = abs(nx - rx) + abs(ny - ry)
                d2 = abs(ox - rx) + abs(oy - ry)
                val = d2 - d1
                if val > best_here:
                    best_here = val
            if best_here > best_val:
                best_val = best_here
                best_move = [dx, dy]
        return best_move

    tx, ty = w - 1, h - 1
    if ox > sx:
        tx = 0
    if oy > sy:
        ty = 0
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]