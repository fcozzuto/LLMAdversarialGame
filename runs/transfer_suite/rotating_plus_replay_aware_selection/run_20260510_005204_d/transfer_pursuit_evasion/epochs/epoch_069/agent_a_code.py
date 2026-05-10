def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)
    we_pursuer = not we_evader

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        p = 0
        for i in (-1, 0, 1):
            xi = x + i
            if xi < 0 or xi >= w: continue
            for j in (-1, 0, 1):
                yj = y + j
                if yj < 0 or yj >= h: continue
                if (xi, yj) in blocked:
                    p += 2 if (i == 0 and j == 0) else 1
        return p

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
    target_x, target_y = best_corner

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in blocked:
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_to_corner = cheb(nx, ny, target_x, target_y)
        pen = obst_pen(nx, ny)

        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy magnitude, then lex order
        tie = (abs(dx), abs(dy), dx, dy)

        if we_pursuer:
            score = d_opp * 10 + pen * 7 + d_to_corner * 0.1
            better = (best_score is None) or (score < best_score) or (score == best_score and tie < best_tie)
        else:
            score = -d_opp * 10 + pen * 7 - d_to_corner * 0.5
            better = (best_score is None) or (score > best_score) or (score == best_score and tie < best_tie)

        if better:
            best_score = score
            best_tie = tie
            best_move = [dx, dy]

    return best_move