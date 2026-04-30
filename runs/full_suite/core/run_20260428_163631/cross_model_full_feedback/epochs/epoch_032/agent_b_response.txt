def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
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

    def manhattan(a, b):
        ax, ay = a; bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Prefer moving toward nearest resource if available, else toward opponent to block
    target_resources = resources if resources else []
    best_move = None
    best_score = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0
        if target_resources:
            # distance to nearest resource after move
            dist = min(manhattan((nx, ny), r) for r in target_resources)
            score -= dist * 2
        # consider approaching opponent to block
        dist_opp = manhattan((nx, ny), (ox, oy))
        score -= dist_opp
        # keep away from obstacles (not on them by legality)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]