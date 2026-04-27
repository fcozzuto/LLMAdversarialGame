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

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    target = None
    bestd = 10**9
    for (rx, ry) in resources:
        d = cheb(mx, my, rx, ry)
        if d < bestd:
            bestd = d
            target = (rx, ry)

    # If no resource, head toward center area away from opponent
    if target is None:
        tx, ty = 0, 0
        center_candidates = [(4,4), (3,4), (4,3), (3,3)]
        bestc = None
        for cx, cy in center_candidates:
            if ok(cx, cy):
                disto = max(abs(mx - cx), abs(my - cy))
                distp = max(abs(ox - cx), abs(oy - cy))
                score = distp - disto
                if bestc is None or score > bestc:
                    bestc = score
                    tx, ty = cx, cy
        target = (tx, ty)

    tx, ty = target if target is not None else (mx, my)

    # Choose move that brings us closer to target while avoiding obstacles and staying within board
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not ok(nx, ny):
            continue
        # prefer moves toward target
        to_target = - (abs(nx - tx) + abs(ny - ty))
        # prefer not moving into opponent's cell
        if (nx, ny) == (ox, oy):
            continue
        # Basic scoring
        score = to_target
        # Encourage approaching center when target equals current
        if target == (mx, my):
            if ok(mx, my):
                score += 0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback to staying if no valid move found
    if best_move is None:
        best_move = (0, 0)
    return [int(best_move[0]), int(best_move[1])]