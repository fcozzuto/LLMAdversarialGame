def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def d_cheb(a, b, c, e):
        dx = a - c
        dy = b - e
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best_gain = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = d_cheb(sx, sy, rx, ry)
            od = d_cheb(ox, oy, rx, ry)
            gain = od - sd
            if gain > best_gain or (gain == best_gain and sd < best_sd):
                best_gain, best_sd = gain, sd
                target = (rx, ry)
    else:
        cx = 3 if sx < w // 2 else 4
        cy = 3 if sy < h // 2 else 4
        target = (cx, cy)

    tx, ty = target
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_d = d_cheb(nx, ny, tx, ty)
        opp_d = d_cheb(ox, oy, tx, ty)
        if resources and (nx, ny) in set((p[0], p[1]) for p in resources):
            self_d = 0
        new_opp_d = d_cheb(ox, oy, tx, ty)
        opp_adv = new_opp_d - self_d
        val = opp_adv * 10 - self_d * 2 + (1 if (dx == 0 and dy == 0) else 0) * 0
        if opp_d - d_cheb(nx, ny, tx, ty) < -1:
            val -= 3
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]