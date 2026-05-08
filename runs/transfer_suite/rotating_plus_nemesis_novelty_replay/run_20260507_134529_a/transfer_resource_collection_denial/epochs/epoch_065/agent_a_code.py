def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            key = (v, -abs(nx - ox) - abs(ny - oy), nx, ny)
            if key > (best[0], -abs(best[1] - ox) - abs(best[2] - oy), best[1], best[2]):
                best = (v, nx, ny)
        return [best[1] - sx, best[2] - sy]

    best_key = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        chosen = None
        chosen_key = None
        # Pick the most "contested" target for us after this move.
        for i, r in enumerate(resources):
            rx, ry = r[0], r[1]
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Maximize opponent advantage we remove: opp_d - self_d
            # Then prefer smaller self_d; deterministic tie on (rx, ry, i).
            k = (opp_d - self_d, -self_d, -rx, -ry, -i)
            if chosen_key is None or k > chosen_key:
                chosen_key = k
                chosen = (rx, ry)

        # Overall choose move that yields best contested key; tie-break by move lexicographic.
        overall_key = (chosen_key[0], chosen_key[1], chosen[0], chosen[1])
        move_key = (overall_key, -dx, -dy, dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]