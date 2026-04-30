def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def score_pos(x, y):
        if not resources:
            cx, cy = w // 2, h // 2
            return -cheb(x, y, cx, cy), cheb(x, y, cx, cy), 0
        best = None
        for rx, ry in resources:
            myd = cheb(x, y, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Favor resources where we are closer; if behind, prefer reducing opponent's lead.
            adv = od - myd
            # Small tie-breakers: shorter my distance, and slight preference to closer-to-opponent targets.
            key = (adv, -myd, -cheb(ox, oy, rx, ry))
            if best is None or key > best[0]:
                best = (key, myd, adv)
        key, myd, adv = best
        # Convert key to a single comparable tuple for move selection
        return (key[0], key[1], key[2]), myd, adv

    best_move = None
    for dx, dy, nx, ny in legal:
        key, myd, adv = score_pos(nx, ny)
        cand = (key, -myd, -adv, dx, dy)
        if best_move is None or cand > best_move[0]:
            best_move = (cand, [dx, dy])

    return best_move[1]