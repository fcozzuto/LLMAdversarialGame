def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    obs = set()
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    if not res:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_adv = -10**18
    best_our = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        move_adv = -10**18
        move_our = 10**18
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            if adv > move_adv or (adv == move_adv and our_d < move_our):
                move_adv = adv
                move_our = our_d
        if (move_adv > best_adv) or (move_adv == best_adv and move_our < best_our) or (
            move_adv == best_adv and move_our == best_our and (dx, dy) != (0, 0) and best_move == [0, 0]
        ):
            best_adv = move_adv
            best_our = move_our
            best_move = [dx, dy]
    return best_move