def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def legal_moves():
        out = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                out.append((dx, dy))
        return out

    legal = legal_moves()
    if not legal:
        return [0, 0]

    # Target selection: try to secure a resource we can reach no later than opponent;
    # if none, race the opponent's closest target.
    best_gap = None
    best_opp = None
    target = None
    for rx, ry in resources:
        d_me = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        gap = d_me - d_opp
        if best_gap is None or gap < best_gap or (gap == best_gap and d_me < best_me):
            best_gap = gap
            best_me = d_me
            target = (rx, ry)
        if best_opp is None or d_opp < best_opp:
            best_opp = d_opp
            urgent = (rx, ry)

    if best_gap is None:
        target = resources[0]
    else:
        if best_gap <= 0:
            pass
        else:
            target = urgent

    tx, ty = target

    # Move choice: reduce distance to target; tie-break by also slightly increasing separation from opponent.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_now = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        key = (d_now, -opp_d, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]