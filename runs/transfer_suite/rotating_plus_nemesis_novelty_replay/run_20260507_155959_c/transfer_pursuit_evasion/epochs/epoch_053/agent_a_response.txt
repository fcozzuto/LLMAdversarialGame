def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves.sort()  # deterministic tie-break

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        d_ctr = abs(nx - cx) + abs(ny - cy)
        key = (d_op, d_ctr, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move