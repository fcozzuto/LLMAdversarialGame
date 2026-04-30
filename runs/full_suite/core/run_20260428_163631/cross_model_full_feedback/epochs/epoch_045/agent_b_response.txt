def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            d_opp = man((nx, ny), (ox, oy))
            d_res = min(man((nx, ny), r) for r in resources)
            close_to_res = 1 if d_res == 0 else 0
            score = (-abs(nx - sx) - abs(ny - sy))  + ( -d_opp ) + (close_to_res * 10)
            if best is None or score > bestv:
                best = (dx, dy, nx, ny)
                bestv = score
        if best is not None:
            return [best[0], best[1]]

    # If no resources or no good move toward resource, move toward center while avoiding opponent
    center_x, center_y = w // 2, h // 2
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        dist_center = -abs(nx - center_x) - abs(ny - center_y)
        dist_opp = -abs(nx - ox) - abs(ny - oy)
        score = dist_center + dist_opp
        if best is None or score > bestv:
            best = (dx, dy, nx, ny)
            bestv = score
    if best is not None:
        return [best[0], best[1]]

    # Fallback
    return [0, 0]