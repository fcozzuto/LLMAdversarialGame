def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Deterministic move order: prefer staying diagonal-ish toward resources
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not is_free(nx, ny):
            continue

        min_my = 10**9
        min_op = 10**9
        capture = 0
        row_pen = 0

        # Sweep-row opponent: penalize moving into its row unless it is already unreachable.
        if oy == ny:
            row_pen = 2.5

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if myd < min_my:
                min_my = myd
            if od < min_op:
                min_op = od
            if nx == rx and ny == ry:
                capture += 1

        if min_my == 10**9:
            continue

        # Main objective: be closer than opponent to the next-best contested resource.
        adv = min_op - min_my  # positive is good
        closeness = 1.0 / (1 + min_my)
        opp_pressure = 1.0 / (1 + min_op)

        score = 10.0 * adv + 4.0 * closeness - 2.0 * opp_pressure - row_pen
        if capture:
            score += 25.0 * capture

        if score > best_score:
            best_score = score
            best_move = [dxm, dym]
        elif score == best_score:
            if [dxm, dym] < best_move:
                best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]