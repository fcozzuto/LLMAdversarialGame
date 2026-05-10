def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_adv(px, py):
        best_v = -10**18
        best_sd = 10**18
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            v = od - sd
            if v > best_v or (v == best_v and sd < best_sd):
                best_v = v
                best_sd = sd
        return best_v, best_sd

    cur_v, _ = best_adv(sx, sy)
    best_move = (0, 0)
    best_tuple = (-10**30, 10**18, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        v, sd = best_adv(nx, ny)
        step_gain = v - cur_v
        # Prefer higher advantage; if equal, closer to resource; if still equal, prefer moves that reduce self-opponent manhattan.
        opp_dist = man(nx, ny, ox, oy)
        tup = (v, -sd, -opp_dist)
        if tup > best_tuple:
            best_tuple = tup
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]