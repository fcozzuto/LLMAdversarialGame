def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mindist(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                m += 1
        return m

    self_evader = ("evader" in self_role) or ("escape" in self_role)
    opp_evader = ("evader" in opp_role) or ("escape" in opp_role)
    evader = self_evader or (not opp_evader and ("evader" not in self_role) and ("purs" not in self_role and "hunter" not in self_role and "chaser" not in self_role and "pursuer" not in self_role))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = mindist(nx, ny)
        mob_o = mobility(ox, oy)
        # small obstacle-aware bias to avoid hugging blocked areas deterministically
        mob_self = mobility(nx, ny)
        if evader:
            # maximize separation; also prefer moves with lower opponent mobility impact (harder for pursuer)
            score = (d, -mob_self, -mob_o, -abs(nx - ox) - abs(ny - oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            # pursue: minimize distance; also prefer reducing opponent mobility (limits escape)
            score = (-d, mob_o, -mob_self, -abs(nx - ox) - abs(ny - oy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]