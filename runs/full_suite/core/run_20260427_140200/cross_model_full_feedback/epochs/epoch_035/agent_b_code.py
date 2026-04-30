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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0), (1,  0),
            (-1,  1), (0,  1), (1,  1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_dx = 0
    best_dy = 0
    best_score = None

    # If there are resources, head toward the closest one while considering opponent.
    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # distance to closest resource from new pos
            d_me = min((man(nx, ny, rx, ry) for rx, ry in resources), default=999)
            # distance from opponent to closest resource
            d_opp = min((man(ox, oy, rx, ry) for rx, ry in resources), default=999)
            score = (d_opp - d_me) * 3 - d_me
            if best_score is None or score > best_score:
                best_score = score
                best_dx = dx
                best_dy = dy
        if best_score is not None:
            return [best_dx, best_dy]

    # Fallback: move toward center or away from opponent to avoid stalemate.
    cx, cy = w // 2, h // 2
    cand = None
    cand_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # prefer moving closer to center and away from opponent
        d_center = man(nx, ny, cx, cy)
        d_opp = man(nx, ny, ox, oy)
        score = -d_center + d_opp
        if cand_score is None or score > cand_score:
            cand_score = score
            cand = (dx, dy)
    if cand is not None:
        return [cand[0], cand[1]]

    # As a last resort, stay still
    return [0, 0]