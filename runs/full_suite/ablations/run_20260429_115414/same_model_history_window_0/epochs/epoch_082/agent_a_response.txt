def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obstacle_set = set((p[0], p[1]) for p in obstacles)
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        # fallback: move away from opponent deterministically
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        return [dx, dy]
    # determine best move by targeting a resource we can reach sooner than opponent
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue
        # local evaluation: choose resource that maximizes advantage
        local_best = -10**9
        for rx, ry in resources:
            myd = abs(nx - rx) + abs(ny - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            # Prefer taking resources sooner, and also moving closer overall
            adv = opd - myd
            # Encourage blocking: if opponent would be closer to that resource after move, reduce
            block_pen = 0
            if adv < 0:
                block_pen = -2 * (-adv)
            # Prefer resources nearer to me when advantages tie
            val = 10 * adv - 0.1 * myd + block_pen
            if val > local_best:
                local_best = val
        # small tie-breakers to move along grid deterministically
        tie = 0
        if dx != 0:
            tie += -0.01 * abs(dy) - 0.001 * (0 if dx > 0 else 1)
        else:
            tie += -0.001 * (0 if dy == 0 else (0 if dy > 0 else 1))
        total = local_best + tie
        if total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)
    # If all moves blocked, stay
    return [int(best_move[0]), int(best_move[1])]