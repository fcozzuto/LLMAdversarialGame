def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    my_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    is_pursuer = ("pursuer" in my_role) or ("tagger" in my_role) or ("pursuer" in role) or ("tagger" in role)
    is_evader = ("evader" in my_role) or ("runner" in my_role) or ("evader" in role) or ("runner" in role)
    if is_pursuer and is_evader:
        is_pursuer = False

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    best_d = None
    best_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        if best_d is None:
            best_d = d
            best_moves = [(dx, dy)]
        else:
            if is_pursuer:
                better = d < best_d
            else:
                better = d > best_d
            if better:
                best_d = d
                best_moves = [(dx, dy)]
            elif d == best_d:
                best_moves.append((dx, dy))

    if not best_moves:
        return [0, 0]
    best_moves.sort()
    return [best_moves[0][0], best_moves[0][1]]