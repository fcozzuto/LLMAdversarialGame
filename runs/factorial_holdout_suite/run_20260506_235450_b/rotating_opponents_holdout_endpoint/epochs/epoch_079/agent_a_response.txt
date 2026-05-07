def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = tr <= 5

    # Choose a target that we can likely secure earlier; otherwise pick a closest one.
    best_t = None
    best_v = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # If we can beat opponent, prioritize; else still prefer closer.
        v = (0 if sd <= od else 1, (sd - od), sd if not endgame else 0, x * 100 + y)
        if best_v is None or v < best_v:
            best_v, best_t = v, (x, y)
    tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nsd = cheb(nx, ny, tx, ty)
                nod = cheb(nx, ny, ox, oy)
                # Prefer decreasing distance to target; small penalty for approaching opponent.
                # Tie-break deterministically by lexicographic move.
                val = (nsd, -nod if endgame else nod, abs(dx) + abs(dy), dx, dy)
                moves.append((val, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda z: z[0])
    return [moves[0][1], moves[0][2]]