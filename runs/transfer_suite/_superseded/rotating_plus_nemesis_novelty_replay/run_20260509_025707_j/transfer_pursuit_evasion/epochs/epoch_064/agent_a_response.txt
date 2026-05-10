def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evade = is_evader(observation.get("self_role"))
    opp_evade = is_evader(observation.get("opponent_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def opp_next(myx, myy):
        best = None
        bestv = None
        for ddx, ddy in dirs:
            nx, ny = ox + ddx, oy + ddy
            if not valid(nx, ny):
                continue
            v = dist2(nx, ny, myx, myy)
            if opp_evade:
                key = v  # maximize
                better = (bestv is None) or (key > bestv)
            else:
                key = v  # minimize
                better = (bestv is None) or (key < bestv)
            if better:
                bestv = key
                best = (nx, ny)
        if best is None:
            return (ox, oy)
        return best

    best_move = [0, 0]
    best_rank = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        px, py = opp_next(nx, ny)
        captured = (nx == px and ny == py)
        if captured:
            rank = (0, 0)
        else:
            d = dist2(nx, ny, px, py)
            rank = (1, d if not self_evade else -d)  # pursuer: minimize, evader: maximize
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]