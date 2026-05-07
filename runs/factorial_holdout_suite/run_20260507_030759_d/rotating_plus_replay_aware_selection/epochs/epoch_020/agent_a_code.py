def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best_dx = 0
    best_dy = 0
    best_score = -10**18

    # Strategy: always chase a resource where we are meaningfully closer than the opponent.
    # Score each candidate move by the best resource it could help secure.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        move_best = -10**18
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            if (nx, ny) == (rx, ry):
                val = 10**9
            else:
                # Prefer resources we can likely secure first; penalize those opponent is closer to.
                val = (opp_d - my_d) * 1000 - my_d * 5
                # Mild bias to avoid being at a dead-end relative to opponent (resource denial behavior).
                val += (my_d - opp_d) * 2

            if val > move_best:
                move_best = val

        # Tie-break: reduce distance to the single closest resource (deterministic).
        if move_best > best_score:
            best_score = move_best
            best_dx, best_dy = dx, dy
        elif move_best == best_score:
            # Deterministic tie-break without randomness
            # Prefer the move with smallest min distance to any resource.
            cur_min = 10**9
            nxt_min = 10**9
            for rx, ry in resources:
                cur_min = min(cur_min, man(sx, sy, rx, ry))
                nxt_min = min(nxt_min, man(nx, ny, rx, ry))
            if nxt_min < cur_min:
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]