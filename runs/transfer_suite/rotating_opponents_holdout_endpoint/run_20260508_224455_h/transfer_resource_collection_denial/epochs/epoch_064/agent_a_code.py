def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inb(x, y): 
        return 0 <= x < gw and 0 <= y < gh
    def valid(x, y): 
        return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): 
        return abs(x1 - x2) + abs(y1 - y2)

    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None  # (score, -tie, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine keeps in place; emulate deterministically
        near_pen = 0.25 * obst_near(nx, ny)
        best_for_move = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            if not valid(rx, ry) and (rx, ry) not in obstacles:
                continue
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources where we're closer than opponent; discourage slow paths.
            sc = (d_opp - d_me) - 0.08 * d_me - near_pen
            if sc > best_for_move or (sc == best_for_move and d_me < best_dist):
                best_for_move, best_dist = sc, d_me
        tie = -best_dist
        cand = (best_for_move, tie, dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[2]), int(best[3])]