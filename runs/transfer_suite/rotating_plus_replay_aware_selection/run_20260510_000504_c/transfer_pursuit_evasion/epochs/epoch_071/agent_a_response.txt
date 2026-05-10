def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("evader" in self_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_proximity(x, y):
        if not obstacles:
            return 0
        m = 10**9
        for a, b in obstacles:
            d = abs(x - a) + abs(y - b)
            if d < m:
                m = d
        return m if m != 10**9 else 0

    # Evader: run to farthest corner from pursuer; Pursuer: chase to minimize distance.
    target_corner = None
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        bestc = -1
        for cx, cy in corners:
            d = manhattan(cx, cy, ox, oy)
            if d > bestc:
                bestc = d
                target_corner = (cx, cy)
        tcx, tcy = target_corner
    else:
        tcx, tcy = ox, oy

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = manhattan(nx, ny, ox, oy)
        d_tar = manhattan(nx, ny, tcx, tcy)
        prox = obstacle_proximity(nx, ny)

        if is_evader:
            # maximize distance from opponent, also prefer moving toward chosen farthest corner, avoid obstacles.
            score = (d_opp * 10) + (-d_tar) + (prox * 0.5)
        else:
            # minimize distance to opponent; slight preference to keep away from obstacles' immediate neighbors.
            score = (-d_opp * 10) + (-d_tar * 0.1) + (prox * 0.2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move in ([-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, 1]) else [0, 0]