def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            score = (man(nx, ny, ox, oy), -man(nx, ny, ox, oy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_res = None
    best_val = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # Prefer resources we are closer to (opp_d - self_d large), but avoid too-far targets
        val = (opp_d - self_d) * 100 - self_d
        if best_val is None or val > best_val or (val == best_val and self_d < best_res[0]):
            best_val = val
            best_res = (self_d, rx, ry)

    _, tx, ty = best_res

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Drive toward chosen contested resource; also try not to get too close to opponent
        score = (-d_to, d_opp)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]