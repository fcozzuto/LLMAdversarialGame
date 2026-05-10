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
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (x + ax, y + ay) in obstacles:
                        cnt += 1
        return cnt

    def wall_penalty(x, y):
        d = min(x, y, (w - 1) - x, (h - 1) - y)
        return 0 if d >= 2 else (2 - d) * 1.2  # discourage hugging walls

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        center = -((nx - cx) ** 2 + (ny - cy) ** 2)  # prefer center to cut off wall-running
        score = (-dist) + 0.10 * center - 0.35 * obstacle_adj(nx, ny) - 0.40 * wall_penalty(nx, ny)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best