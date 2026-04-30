def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    op = (ox, oy)
    best_move = None
    best_score = -10**9

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        pos = (nx, ny)

        # heuristic: minimize distance to opponent if far, but also approach closest resource
        d_to_op = dist(pos, op)

        # closest resource after move
        if resources:
            d_to_res = min(dist(pos, r) for r in resources)
        else:
            d_to_res = 10**6

        # simple scoring: prefer closer to resources, but avoid clustering with opponent
        score = -d_to_res * 2 + -d_to_op

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]