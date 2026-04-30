def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def nearest_obst_pen(nx, ny):
        # Penalize proximity to obstacles to reduce detours into dead areas
        best = 10**9
        for (px, py) in obst:
            dd = abs(nx - px) if abs(nx - px) > abs(ny - py) else abs(ny - py)
            if dd < best: best = dd
        return best  # lower is worse

    # Target selection (materially different from pure "reach advantage"): maximize advantage,
    # but if we're not ahead anywhere, go for the resource farthest from opponent.
    target = None
    best_adv = -10**18
    best_op_d = -10**18
    for rx, ry in resources:
        myd = d2(x, y, rx, ry)
        opd = d2(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv:
            best_adv = adv
            target = (rx, ry)
        od = opd
        if od > best_op_d:
            best_op_d = od
            best_op_t = (rx, ry)

    if not resources:
        target = (ox, oy)  # fallback
    else:
        if best_adv <= 0:  # no reach advantage: prioritize denying opponent by targeting farthest-from-them
            target = best_op_t

    tx, ty = target
    if tx == x and ty == y and resources:
        return [0, 0]

    legal = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))

    # If no legal moves (shouldn't happen), stay.
    if not legal:
        return [0, 0]

    # Move scoring: progress to target, keep distance from opponent, and avoid obstacle-adjacent traps.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        prog = -d2(nx, ny, tx, ty)
        opp_sep = d2(nx, ny, ox, oy)
        obst_pen = nearest_obst_pen(nx, ny)
        # Convert obstacle distance to penalty: being adjacent is costly.
        # obst_pen==0 impossible (cell blocked), obst_pen==1 is adjacency.
        trap_pen = 0 if obst_pen >= 2 else (4 - obst_pen) * 10
        score = prog * 3 + opp_sep * 0.02 - trap_pen
        # Deterministic tie-breaker: prefer staying slightly less often, then lexicographic dx,dy
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]