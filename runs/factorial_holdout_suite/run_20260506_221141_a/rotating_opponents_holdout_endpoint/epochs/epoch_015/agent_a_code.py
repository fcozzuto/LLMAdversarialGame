def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def clip_step(nx, ny):
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        return nx, ny

    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return (-10**9, 10**9)
        if not resources:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return (0, man(nx, ny, cx, cy))
        best_adv = -10**9
        best_dist = 10**9
        # Greedy one-step planning: after moving, choose the resource where we gain most over opponent.
        for tx, ty in resources:
            self_d = man(nx, ny, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_dist):
                best_adv = adv
                best_dist = self_d
        # Small preference for getting closer even when tied.
        return (best_adv, best_dist)

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = clip_step(sx + dx, sy + dy)
        sc = move_score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]