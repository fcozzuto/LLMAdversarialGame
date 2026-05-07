def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = -10**18

    # Select resource by race advantage first; add a mild center preference to reduce dithering.
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds  # positive if we can arrive earlier
        center_bias = -0.02 * (abs(rx - cx) + abs(ry - cy))
        if advantage > 0:
            # When we can win, prioritize larger advantage and lower self distance.
            score = 1000 * advantage - 2 * ds + center_bias
        else:
            # When we might lose, still take opportunities where opponent can't reach instantly and path is short.
            score = 20 * advantage - 1.2 * ds + center_bias
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Greedy one-step toward target with obstacle-aware tie-break, also try to keep moving in the "useful" direction.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            step_to_target = -d
            # If opponent is close, prefer steps that reduce our distance more than theirs would change (local proxy).
            danger = 0
            for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx - 1, ny - 1), (nx + 1, ny - 1), (nx - 1, ny + 1)):
                if (ax, ay) in obstacles:
                    danger += 1
            # Keep from oscillating: mild bias toward progressing away from our start corner when close.
            prog = 0
            if (sx, sy) == (0, 0) or (sx, sy) == (w - 1, h - 1):
                prog = -(cheb(nx, ny, tx, ty) - cheb(sx, sy, tx, ty)) * 0.1
            # Staying allowed: consider 0,0 if all moves are bad.
            moves.append((step_to_target - 5 * danger + prog + (1 if cheb(nx, ny, ox, oy) > cheb(sx, sy, ox, oy) else 0), dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(reverse=True, key=lambda t: t[0])
    return [int(moves[0][1]), int(moves[0][2])]