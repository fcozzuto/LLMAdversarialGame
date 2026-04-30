def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def chebyshev(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_move = None
    best_score = None

    # Priority: grab closest resource if any, else approach opponent to contest
    if resources:
        target = min(resources, key=lambda r: dist((sx, sy), r))
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            nd = dist((nx, ny), target)
            if best_score is None or nd < best_score:
                best_score = nd
                best_move = (dx, dy)
        if best_move is None:
            best_move = (0, 0)
        return [best_move[0], best_move[1]]
    else:
        # No resources: move to reduce distance to opponent, with slight bias to avoid cliffs
        best_move = None
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = dist((nx, ny), (ox, oy))
            if best_score is None or d < best_score:
                best_score = d
                best_move = (dx, dy)
        if best_move is None:
            best_move = (0, 0)
        return [best_move[0], best_move[1]]