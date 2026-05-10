def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursu" in self_role) or ("chase" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    pref = [(0,-1), (-1,0), (1,0), (0,1), (-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
    moves = pref

    corners = [(0,0), (0,h-1), (w-1,0), (w-1,h-1)]
    if corners:
        far_corner = max(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy))
    else:
        far_corner = (0, 0)

    best = None
    best_score = None
    best_tiebreak = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if is_pursuer:
            score = d
            # secondary: move along toward opponent in manhattan sense
            tie = -(abs(nx-ox) + abs(ny-oy))
        else:
            score = -d  # maximize distance
            # secondary: head toward farthest corner from opponent
            tie = -(abs(nx-far_corner[0]) + abs(ny-far_corner[1]))
        if best_score is None or score < best_score or (score == best_score and tie < best_tiebreak):
            best_score = score
            best_tiebreak = tie
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]