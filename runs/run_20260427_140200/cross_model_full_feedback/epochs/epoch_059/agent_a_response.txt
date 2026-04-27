def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]
    # Determine a "dominant" target: closest resource by distance, tie by resource score proxy (closer to center).
    if resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_t = None
        best_td = None
        for tx, ty in resources:
            d = cheb(sx, sy, tx, ty)
            td = d * 1000 + int(abs(tx - cx) + abs(ty - cy))
            if best_td is None or td < best_td:
                best_td = td
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No resources visible: move to a safe "pivot" near center but away from opponent.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Heuristic scoring for each move: progress to target, avoid opponent, avoid locking into walls by preferring moves with more exits.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)

        # Discourage moving adjacent to opponent too often (encourages safer resource capture).
        opp_pen = 0
        if d_to_o <= 1:
            opp_pen = 900
        elif d_to_o == 2:
            opp_pen = 250
        elif d_to_o == 3:
            opp_pen = 80

        # Prefer moves that increase local mobility (more legal neighbor squares).
        mob = 0
        for ddx, ddy in moves:
            mx, my = nx + ddx, ny + ddy
            if legal(mx, my):
                mob += 1

        # If opponent is also heading toward the same region, bias away by maximizing distance to opponent when close.
        # Also slight preference for reducing distance directly.
        progress = cheb(sx, sy, tx, ty) - d_to_t
        score = (-d_to_t) + progress * 5 + mob * 2 - opp_pen

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move