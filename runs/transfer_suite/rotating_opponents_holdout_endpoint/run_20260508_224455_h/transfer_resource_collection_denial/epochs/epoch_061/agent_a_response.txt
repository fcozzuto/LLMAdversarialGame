def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obs_list)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    def first_target():
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer guaranteed advantage; otherwise maximize advantage margin.
            # Tie-break: closer-to-finish then by coords for determinism.
            guaranteed = 1 if (sd + 1 <= od) else 0
            key = (guaranteed, od - sd, -(sd), -((rx * 31 + ry) % 997))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = first_target()
    if target is None:
        return [0, 0]

    tx, ty = target
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)

        # Try to keep/improve advantage; penalize congestion near obstacles.
        # Also lightly discourage stepping into squares that would reduce the gap less than alternatives.
        gap = opp_d - self_d
        adv = 1 if (self_d + 1 <= opp_d) else 0
        obst = adj_obst(nx, ny)

        # Secondary idea: if we can't secure, still prefer moves that reduce distance to any resource
        # that the opponent is currently closer to (counter-priority).
        steal_r = 0
        if resources:
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                if (cheb(nx, ny, rx, ry) < cheb(ox, oy, rx, ry)) and (cheb(sx, sy, rx, ry) >= cheb(ox, oy, rx, ry)):
                    steal_r += 1

        val = (adv, gap, -self_d, steal_r, -obst, (dx == 0 and dy == 0) * -1)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move