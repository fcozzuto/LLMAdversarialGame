def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr)
    opp_is_pursuer = ("pursuer" in orr) or ("chaser" in orr) or ("seeker" in orr)

    # If roles are unclear, assume we are pursuer when opponent is not.
    if (self_is_pursuer and not opp_is_pursuer) or (self_is_pursuer and opp_is_pursuer):
        mode = "toward"
    elif (opp_is_pursuer and not self_is_pursuer):
        mode = "away"
    else:
        mode = "toward"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny)
        # Toward pursues opponent (minimize distance); away evades (maximize distance).
        val = -dist if mode == "toward" else dist
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move