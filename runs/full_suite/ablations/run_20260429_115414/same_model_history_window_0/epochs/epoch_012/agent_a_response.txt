def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best_res = resources[0]
        best_val = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            val = (od - sd) * 10 - sd
            if best_val is None or val > best_val:
                best_val = val
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                score = -10**9
            else:
                dist = man(nx, ny, tx, ty)
                self_to_opp = man(nx, ny, ox, oy)
                opp_to_target = man(ox, oy, tx, ty)
                score = -dist * 5 + (opp_to_target - self_to_opp)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move