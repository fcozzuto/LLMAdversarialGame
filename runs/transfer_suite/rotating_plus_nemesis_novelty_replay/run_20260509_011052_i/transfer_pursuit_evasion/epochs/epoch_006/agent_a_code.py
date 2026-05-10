def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = str(observation.get("self_role", "pursuer")).lower()
    evade = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    cap_r = int(observation.get("capture_radius", 0) or 0)

    def dist_cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = dist_cheb(nx, ny, ox, oy)
        score = -d if evade else d
        if cap_r > 0:
            score += 2 if d <= cap_r else 0
        if best is None or score > bestv:
            bestv = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best