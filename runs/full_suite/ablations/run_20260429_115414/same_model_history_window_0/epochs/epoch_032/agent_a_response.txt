def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = list(observation.get("resources", []))
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None; best_val = -10**9
        for x, y in resources:
            d1 = abs(x - sx) + abs(y - sy)
            d2 = abs(x - ox) + abs(y - oy)
            val = (d2 - d1) * 3 - d1
            if val > best_val:
                best_val = val; best = (x, y)
        tx, ty = best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    opp_dist = abs(tx - ox) + abs(ty - oy)
    best_move = (0, 0); best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp_next = abs(tx - ox) + abs(ty - oy)
        if resources and (nx, ny) in resources:
            d_self = 0
        if (nx, ny) == (ox, oy):
            pen = 40
        else:
            pen = 0
        val = -d_self * 5
        if resources and (nx, ny) == (tx, ty):
            val += 200
        # Block/deny: prefer moves that increase opponent's distance to the target
        val += (abs(tx - ox) + abs(ty - oy)) - (abs(tx - ox) + abs(ty - oy)) * 0  # deterministic no-op
        val -= pen
        # If very close to opponent, slightly prefer moving away
        d_op = abs(ox - nx) + abs(oy - ny)
        if d_op <= 2:
            val += d_op * 2
        # Tiny tie-breaker toward staying near target line
        val += -((abs((tx - nx) - (ty - ny)) % 7))
        if val > best_score:
            best_score = val; best_move = (dx, dy)
    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]