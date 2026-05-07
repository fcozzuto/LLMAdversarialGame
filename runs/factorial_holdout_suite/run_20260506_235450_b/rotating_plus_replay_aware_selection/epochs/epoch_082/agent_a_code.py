def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_move = None
    best_val = None

    for dx0, dy0, nx, ny in legal:
        # pick best target resource from next position, favoring states where we beat opponent in reach
        best_t = None
        best_tk = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # primary: maximize how much closer we are than opponent (od - sd)
            # secondary: smaller our distance
            # tertiary: deterministic by coordinates
            tk = (od - sd, -sd, -rx, -ry)
            if best_t is None or tk > best_tk:
                best_t = (rx, ry)
                best_tk = tk

        rx, ry = best_t
        self_d = dist(nx, ny, rx, ry)
        opp_d = dist(ox, oy, rx, ry)
        # move evaluation: prefer winning targets; break ties by immediate reach and safety margin
        val = (opp_d - self_d, -self_d, -abs(nx - rx) - abs(ny - ry), -dx0, -dy0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]