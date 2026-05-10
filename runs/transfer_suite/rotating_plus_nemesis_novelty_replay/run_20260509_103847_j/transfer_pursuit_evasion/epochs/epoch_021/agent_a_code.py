def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    role = observation.get("self_role", "pursuer")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def step_greedy(posx, posy, flee_fromx, flee_fromy):
        best = (posx, posy)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = posx + dx, posy + dy
            if not inb(nx, ny):
                continue
            # evader: maximize distance from flee-from
            v = dist2(nx, ny, flee_fromx, flee_fromy)
            if v > bestv or (v == bestv and (nx, ny) < best):
                bestv = v
                best = (nx, ny)
        return best

    tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))  # opponent escape corner
    best_move = (0, 0)
    best_score = -10**18

    for dx0, dy0 in deltas:
        nx0, ny0 = sx + dx0, sy + dy0
        if not inb(nx0, ny0):
            continue

        if role == "pursuer":
            # Predict opponent evader move (1 ply) and aim to intercept via corner-midpoint pressure
            nxt_ox, nxt_oy = step_greedy(ox, oy, nx0, ny0)
            # Intercept target: midpoint between predicted evader and its escape corner
            midx, midy = (nxt_ox + tx) / 2.0, (nxt_oy + ty) / 2.0
            score = -dist2(nx0, ny0, nxt_ox, nxt_oy)  # direct catch pressure
            score += -dist2(nx0, ny0, midx, midy) * 0.15  # steer toward interception line
            score += -0.01 * ((nxt_ox - tx) * (nxt_ox - tx) + (nxt_oy - ty) * (nxt_oy - ty))  # limit escape corner
        else:
            # Evader: flee pursuer, but also drift toward the corner farthest from pursuer
            farx, fary = max(corners, key=lambda c: dist2(c[0], c[1], sx, sy))
            flee = dist2(nx0, ny0, ox, oy)
            drift = -dist2(nx0, ny0, farx, fary)
            score = flee + 0.25 * drift

        if score > best_score:
            best_score = score
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]