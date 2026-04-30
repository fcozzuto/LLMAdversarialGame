def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Target: closest resource, else move to a square that keeps distance from opponent but progresses toward center.
    target_list = resources if resources else [(ox, oy)]
    best_move = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # distance to nearest target
        dist_to_target = min(cheb(nx, ny, tx, ty) for (tx, ty) in target_list)
        # distance to opponent (prefer not to collide)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # simple heuristic: prioritize closer to target, but maintain some separation from opponent
        score = (dist_to_target * 2) - dist_to_opp
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        # fallback: stay or move away from opponent if possible
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                best_move = [dx, dy]
                break
        if best_move is None:
            best_move = [0, 0]
    return best_move