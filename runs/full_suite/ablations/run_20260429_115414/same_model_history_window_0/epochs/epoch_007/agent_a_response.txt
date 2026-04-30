def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = observation["resources"]
    opp_weight = 0.15
    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        best = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # prioritize closer to us; penalize if opponent is much closer
            val = ds - opp_weight * do
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # choose move minimizing distance to target, tie-break by maximizing distance from opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d1 = abs(tx - nx) + abs(ty - ny)
        d2 = abs(ox - nx) + abs(oy - ny)
        score = (d1, -d2, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]