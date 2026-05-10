def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obstacle_adj(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    cnt += 1
        return cnt

    def wall_penalty(x, y):
        d = min(x, y, (w - 1) - x, (h - 1) - y)
        return 0.0 if d >= 2 else (2 - d) * 1.3

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dxo = nx - ox
        dyo = ny - oy
        dist2 = dxo * dxo + dyo * dyo
        toward = (sx - ox) * (nx - ox) + (sy - oy) * (ny - oy)  # positive if progress along current direction
        cdist2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = -dist2 + 0.15 * toward - 0.20 * cdist2 - 1.4 * obstacle_adj(nx, ny) - wall_penalty(nx, ny) * 0.8
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move