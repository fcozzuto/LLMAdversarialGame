def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    pref = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    best = None
    best_val = 10**9
    for i in pref:
        dx, dy = moves[i]
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)
        block = 0
        for ax, ay in (-1, 0, 1), (-1, 0, 1):
            pass
        if obstacles:
            for tx in (-1, 0, 1):
                for ty in (-1, 0, 1):
                    if tx == 0 and ty == 0:
                        continue
                    if (nx + tx, ny + ty) in obstacles:
                        block += 1
        val = dist * 10 + block
        if val < best_val:
            best_val = val
            best = [dx, dy]

    if best is not None:
        return best

    for i in pref:
        dx, dy = moves[i]
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
    return [0, 0]