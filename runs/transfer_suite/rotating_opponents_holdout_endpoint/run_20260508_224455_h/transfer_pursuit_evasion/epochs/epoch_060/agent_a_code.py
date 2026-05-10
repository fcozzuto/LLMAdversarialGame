def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(pos):
        x, y = pos
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((nx, ny))
        return out

    my_moves = legal((sx, sy))
    if not my_moves:
        return [0, 0]

    # One-ply minimax: we minimize worst-case distance after opponent replies to maximize distance.
    best_move = my_moves[0]
    best_score = None
    for nx, ny in my_moves:
        opp_moves = legal((ox, oy))
        if not opp_moves:
            score = cheb(nx, ny, ox, oy)
        else:
            worst = -1
            for px, py in opp_moves:
                d = cheb(nx, ny, px, py)
                if d > worst:
                    worst = d
            score = worst
        # Tie-break: prefer moves that also reduce current distance and don't step into low-mobility squares.
        curd = cheb(nx, ny, ox, oy)
        my_mob = len(legal((nx, ny)))
        tie = (score, curd, -my_mob)
        if best_score is None or tie < best_score:
            best_score = tie
            best_move = (nx, ny)

    dx = best_move[0] - sx
    dy = best_move[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]