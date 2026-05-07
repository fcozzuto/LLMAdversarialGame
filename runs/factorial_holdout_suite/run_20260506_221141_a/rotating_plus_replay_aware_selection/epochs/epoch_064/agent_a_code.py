def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    obs_list = observation.get("obstacles") or []
    for p in obs_list:
        obstacles.add((p[0], p[1]))
    res_list = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if res_list:
        best_rx, best_ry = res_list[0][0], res_list[0][1]
        bestv = -10**18
        for rx, ry in res_list:
            sd = manh(sx, sy, rx, ry)
            od = manh(ox, oy, rx, ry)
            v = (od - sd) * 1000 - sd * 3
            if sd == 0:
                v += 10**9
            if v > bestv or (v == bestv and (sd < manh(sx, sy, best_rx, best_ry) or (sd == manh(sx, sy, best_rx, best_ry) and (rx, ry) < (best_rx, best_ry)))):
                bestv = v
                best_rx, best_ry = rx, ry
        tx, ty = best_rx, best_ry
    else:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_target = manh(nx, ny, tx, ty)
        d_to_opp = manh(nx, ny, ox, oy)
        score = (d_to_target, -d_to_opp, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move