def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(a, b):
        dx = abs(a[0]-b[0])
        dy = abs(a[1]-b[1])
        return dx if dx > dy else dy

    def dist(a, b):
        return cheb(a, b)

    def choose_target():
        if not resources:
            return None
        best = None
        best_score = None
        for r in resources:
            da = dist((mx, my), r)
            db = dist((ox, oy), r)
            score = da - db  # prefer closer to me relative to opponent
            if best is None or score > best_score:
                best = r
                best_score = score
        return best

    target = choose_target()

    best_move = (0, 0)
    best_score = None

    def score_move(nx, ny, t):
        if not legal(nx, ny):
            return None
        s = 0
        # Objective: move toward target if any, else approach opponent slightly
        if t is not None:
            s -= dist((nx, ny), t) * 2  # closer to target better
        s -= dist((nx, ny), (ox, oy))  # avoid getting too close to opponent
        # prefer center-ish positions
        center_dx = abs(nx - w//2)
        center_dy = abs(ny - h//2)
        s -= (center_dx + center_dy) * 0.1
        return s

    # evaluate all legal moves
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        s = score_move(nx, ny, target)
        if s is None:
            continue
        if best_score is None or s > best_score:
            best_score = s
            best_move = (dx, dy)

    # If all moves invalid (shouldn't), stay
    dx, dy = best_move
    if not legal(mx + dx, my + dy):
        return [0, 0]
    return [dx, dy]