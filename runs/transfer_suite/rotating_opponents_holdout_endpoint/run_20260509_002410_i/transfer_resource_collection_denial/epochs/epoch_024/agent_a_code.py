def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) != (sx, sy):
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs and (x, y) != (sx, sy):
                resources.append((x, y))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        best = [0, 0]
        best_s = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    continue
                s = man(nx, ny, ox, oy)
                if s > best_s:
                    best_s = s
                    best = [dx, dy]
        return best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = [0, 0]
    best_val = -10**18
    for dx, dy, nx, ny in moves:
        dres = min(man(nx, ny, rx, ry) for rx, ry in resources)
        dop = man(nx, ny, ox, oy)
        val = -dres + 0.1 * dop
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best