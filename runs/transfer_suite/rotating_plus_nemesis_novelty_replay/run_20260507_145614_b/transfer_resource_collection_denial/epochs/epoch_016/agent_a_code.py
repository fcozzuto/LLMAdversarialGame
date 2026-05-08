def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target we can reach before (or at least not after) opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        if not valid(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: win race (ds < do). Secondary: margin. Tertiary: closer overall.
        can_win = 1 if ds < do else 0
        key = (0 if can_win else 1,  # prefer winning races
               -abs(do - ds),        # prefer larger separation
               ds,                   # then prefer closer
               rx, ry)               # then deterministic
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = cheb(sx, sy, tx, ty)

    # Choose move minimizing distance to target, and if tied maximize opponent distance.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Encourage approaching target; discourage allowing opponent to get "much closer" to it.
        no = cheb(ox, oy, tx, ty)
        opp_adv = cheb(ox, oy, tx, ty) - cheb(ox, oy, nx, ny)  # small, stable shaping
        score = (nd, -cheb(ox, oy, nx, ny), -opp_adv, 0 if (dx == 0 and dy == 0) else 1, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # Tiny endgame nudge: if resources very low, bias exact cheb reduction.
    if turns_remaining <= 2 and best_move != (0, 0):
        dx, dy = best_move
        nx, ny = sx + dx, sy + dy
        if cheb(nx, ny, tx, ty) > cur_d:
            return [0, 0]
    return [best_move[0], best_move[1]]