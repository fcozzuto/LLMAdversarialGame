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

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If there are resources, move to reduce distance to the closest resource that is also favorable
    best_dx, best_dy = 0, 0
    if resources:
        # select resource that minimizes max(dist to me, dist from opp to resource) to maximize my gain
        best_r = None
        best_score = None
        for rx, ry in resources:
            d_me = man(sx, sy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            score = d_opp - d_me  # prefer resources closer to me than to opp
            if best_score is None or score > best_score:
                best_score = score
                best_r = (rx, ry)
        if best_r is not None:
            tx, ty = best_r
            # pick move toward this target if legal
            move_candidates = []
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    d = man(nx, ny, tx, ty)
                    move_candidates.append((d, dx, dy))
            if move_candidates:
                move_candidates.sort()
                _, dx, dy = move_candidates[0]
                return [dx, dy]

    # Fallback: head toward center of board or away from opponent to gain space
    target_x = w // 2
    target_y = h // 2
    dx = 0
    if sx < target_x:
        dx = 1
    elif sx > target_x:
        dx = -1
    dy = 0
    if sy < target_y:
        dy = 1
    elif sy > target_y:
        dy = -1

    # try to move toward center if legal; otherwise stay or adjust away from obstacle
    if legal(sx + dx, sy + dy):
        return [dx, dy]

    # try other adjacent cells in a deterministic order
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if legal(nx, ny):
            return [ddx, ddy]

    # stay if no legal move
    return [0, 0]