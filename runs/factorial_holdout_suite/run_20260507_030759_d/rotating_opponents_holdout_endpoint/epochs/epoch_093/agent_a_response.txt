def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_best_adv = -10**18
        move_best_sd = 10**9
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                x, y = r[0], r[1]
                if not isinstance(x, int) or not isinstance(y, int):
                    continue
                if not ok(x, y):
                    continue
                sd = cheb(nx, ny, x, y)
                od = cheb(ox, oy, x, y)
                adv = od - sd
                if adv > move_best_adv or (adv == move_best_adv and sd < move_best_sd):
                    move_best_adv, move_best_sd = adv, sd
        if move_best_sd == 10**9:
            continue
        score = move_best_adv * 1000 - move_best_sd
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move