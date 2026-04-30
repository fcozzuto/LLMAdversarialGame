def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    ox = {tuple(p) for p in obstacles}
    x0, y0 = int(self_pos[0]), int(self_pos[1])
    xo, yo = int(opp_pos[0]), int(opp_pos[1])

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        target = (w // 2, h // 2)
        best = None
        for dx, dy in moves:
            nx, ny = x0 + dx, y0 + dy
            if (nx, ny) in ox:
                continue
            score = -dist((nx, ny), target)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if (nx, ny) in ox:
            nx, ny = x0, y0
            dx, dy = 0, 0
        my_d = {}
        opp_d = {}
        cur = (x0, y0)
        nxt = (nx, ny)
        opp = (xo, yo)
        move_score = -10**9
        for r in resources:
            r = (int(r[0]), int(r[1]))
            d_my = dist(nxt, r)
            d_opp = dist(opp, r)
            adv = d_opp - d_my  # higher means I'm closer
            score_r = adv * 10 - d_my
            if score_r > move_score:
                move_score = score_r
        if best_score is None or move_score > best_score or (move_score == best_score and (dx, dy) < best_move):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]