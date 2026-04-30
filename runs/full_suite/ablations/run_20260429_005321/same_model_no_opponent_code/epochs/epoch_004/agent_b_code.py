def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    obst = set((p[0], p[1]) for p in obstacles)
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    d2 = lambda ax, ay, bx, by: (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def best_target():
        if not resources:
            return ((w - 1) // 2, (h - 1) // 2)
        best_r = resources[0]
        best_s = None
        for rx, ry in resources:
            ds = d2(x0, y0, rx, ry)
            do = d2(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent.
            s = ds - 0.75 * do
            if best_s is None or s < best_s:
                best_s = s
                best_r = (rx, ry)
        return best_r

    tx, ty = best_target()

    # Predict opponent next squares and penalize moving into their immediate reach.
    opp_next = set()
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            opp_next.add((nx, ny))

    # Also compute current adjacency penalty.
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Core: get closer to target while keeping opponent farther from it.
        ds = d2(nx, ny, tx, ty)
        do = d2(ox, oy, tx, ty)

        # Risk: being immediately reachable by opponent.
        danger = 1.2 if (nx, ny) in opp_next else 0.0

        # Risk: moving adjacent to opponent.
        adj = 0.6 * cheb(nx, ny, ox, oy)

        # Encourage staying off obstacles by slightly preferring positions with more open neighbors.
        open_cnt = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) not in obst:
                open_cnt += 1
        openness = -0.02 * (8 - open_cnt)  # higher open_cnt => less penalty

        val = -ds + 0.35 * do - danger - adj + openness

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]