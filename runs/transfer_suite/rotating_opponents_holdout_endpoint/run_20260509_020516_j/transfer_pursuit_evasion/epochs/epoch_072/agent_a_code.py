def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)
    pursuer = ("pursuer" in self_role) or not evader

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    obs_list = list(obstacles)
    def adj_pen(x, y):
        if not obs_list:
            return 0
        p = 0
        for ax, ay in obs_list:
            ddx, ddy = ax - x, ay - y
            if ddx * ddx + ddy * ddy == 1:
                p += 2
            if ddx * ddx + ddy * ddy == 2:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        dist = d2(nx, ny)
        pen = adj_pen(nx, ny)
        if pursuer:
            score = dist * 10 + pen * 3
        else:
            score = -dist * 10 + pen * 3
        scored.append((score, dx, dy, nx, ny))

    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy, _, _ = scored[0]
    return [int(dx), int(dy)]