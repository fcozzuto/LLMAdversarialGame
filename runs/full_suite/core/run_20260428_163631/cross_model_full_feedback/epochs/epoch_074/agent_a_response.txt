def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Deterministic fallback: move toward center while increasing distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy, nx, ny in legal:
            score = (manh(nx, ny, int(cx), int(cy)) * 1.0) - (manh(nx, ny, ox, oy) * 0.15)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    # Greedy with advantage: prefer moves that shorten distance to some resource
    # and where we are at least as close as the opponent.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        dmin = None
        # advantage: how much closer we are than opponent for the best target
        best_adv = None
        # avoid allowing opponent to get a strictly better guaranteed capture next step
        opp_best_d = None
        for rx, ry in resources:
            du = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            if dmin is None or du < dmin:
                dmin = du
            adv = do - du  # positive if we are closer
            if best_adv is None or adv > best_adv:
                best_adv = adv
            if opp_best_d is None or do < opp_best_d:
                opp_best_d = do

        # Tie-breakers:
        # 1) maximize advantage; 2) minimize our distance to nearest resource;
        # 3) keep away from opponent slightly; 4) deterministic ordering via dx,dy sum.
        opp_dist_now = manh(nx, ny, ox, oy)
        # Key: higher best_adv better -> use negative for minimization
        key = ( -best_adv if best_adv is not None else 0,
                dmin if dmin is not None else 0,
                opp_dist_now * 0.05,
                (abs(dx) + abs(dy))*1e-6,
                dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]