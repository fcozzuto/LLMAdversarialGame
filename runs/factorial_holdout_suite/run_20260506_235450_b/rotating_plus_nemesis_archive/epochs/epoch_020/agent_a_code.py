def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]
    if any((sx == r[0] and sy == r[1]) for r in resources):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        can_win = 1 if sd < od else 0
        adv = od - sd
        cand = (can_win, -sd, adv, -tx, -ty)
        if best is None or cand > best:
            best = cand
            best_t = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(ox, oy, tx, ty)
            # prefer getting closer to target; if tied, prefer making opponent further (in same metric)
            score = (-sd2, (od2 - sd2), dx, dy)
            moves.append((score, [dx, dy]))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True, key=lambda x: x[0])
    return moves[0][1]