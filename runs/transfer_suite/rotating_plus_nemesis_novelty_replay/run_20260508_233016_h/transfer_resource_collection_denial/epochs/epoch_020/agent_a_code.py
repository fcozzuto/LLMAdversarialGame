def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_for(nx, ny):
        best_adv = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd
        return best_adv, best_sd

    best_move = [0, 0]
    best_adv, best_sd = best_for(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        adv, sd = best_for(nx, ny)
        if adv > best_adv or (adv == best_adv and sd < best_sd) or (adv == best_adv and sd == best_sd and (dx, dy) < (best_move[0], best_move[1])):
            best_adv, best_sd = adv, sd
            best_move = [dx, dy]
    return best_move