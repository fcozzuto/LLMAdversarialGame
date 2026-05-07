def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def adj_block_cost(x, y):
        c = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = (0, 0, -10**9)

    for dx, dy, nx, ny in legal:
        best_val = -10**12
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # race-first, then immediate distance, then resource centrality, then obstacle safety
            val = (do - ds) * 1000 - ds * 10 + (3 - abs(rx - (w - 1) / 2.0)) + (3 - abs(ry - (h - 1) / 2.0)) - adj_block_cost(nx, ny)
            # slight deterministic bias to keep direction changes from dithering
            val -= (dx * 0.1 + dy * 0.1)
            if val > best_val:
                best_val = val
        # prefer moves that reduce our own distance to the closest contested resource
        if best_val > best_move[2]:
            best_move = (dx, dy, best_val)
        elif best_val == best_move[2]:
            # deterministic tie-break: prefer not-staying if possible, then smaller chebyshev to resources
            if (dx, dy) != (0, 0):
                best_move = (dx, dy, best_val)

    return [int(best_move[0]), int(best_move[1])]