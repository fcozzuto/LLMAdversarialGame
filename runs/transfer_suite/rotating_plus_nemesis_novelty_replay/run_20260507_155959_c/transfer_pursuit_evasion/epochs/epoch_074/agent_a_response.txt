def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.append((int(x), int(y)))
        except Exception:
            pass
    obs_set = set(obstacles)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs_set
    def mdist_to_obs(x, y):
        if not obstacles: return 99
        best = 99
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best: best = d
        return best

    def score(x, y):
        d = abs(x - ox) + abs(y - oy)
        if is_evader:
            return (d, mdist_to_obs(x, y))
        else:
            return (-d, mdist_to_obs(x, y))

    best = None
    best_move = [0, 0]
    # deterministic tie-breaking by move order: keep first with best score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = [dx, dy]

    # if somehow all blocked (shouldn't happen), stay put
    return best_move if best is not None else [0, 0]