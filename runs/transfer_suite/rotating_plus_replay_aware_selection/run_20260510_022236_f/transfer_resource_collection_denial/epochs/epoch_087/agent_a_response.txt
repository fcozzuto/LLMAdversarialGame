def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    tr = int(observation.get("turns_remaining", 0))
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # deterministic fallback; engine would also keep us
        best_for_pos = None
        for rx, ry in valid_res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prioritize "can arrive first", then biggest advantage; tie-break by closer and earlier under turns_remaining
            can = (ds <= do)
            score = (1 if can else 0) * 100000 + (do - ds) * 1000 - ds
            if tr > 0 and ds > tr:
                score -= 20000 + (ds - tr) * 50
            if best_for_pos is None or score > best_for_pos[0]:
                best_for_pos = (score, ds, do, rx, ry)
        score = best_for_pos[0]
        tie = (score, best_for_pos[1], -best_for_pos[2], nx, ny, dx, dy)
        if best_score is None:
            best_score = tie
            best_move = (dx, dy)
        else:
            if tie > best_score:
                best_score = tie
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]