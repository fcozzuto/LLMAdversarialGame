def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def is_pursuer(role):
        r = str(role).lower()
        return "pursuer" in r

    sr = observation.get("self_role", "")
    orr = observation.get("opponent_role", "")
    self_p = is_pursuer(sr)
    opp_p = is_pursuer(orr)

    if self_p and not opp_p:
        i_evader = False
        tx, ty = ox, oy
    elif opp_p and not self_p:
        i_evader = True
        tx, ty = ox, oy
    else:
        i_evader = "evader" in str(sr).lower()
        tx, ty = ox, oy

    obstacles = set(tuple(p) for p in observation.get("obstacles", []) if len(p) == 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        score = -d2 if not i_evader else d2
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]