def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer")
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not self_role and opponent_role:
        pursuer = not ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    tx = 0 if ox == sx else (1 if ox > sx else -1)
    ty = 0 if oy == sy else (1 if oy > sy else -1)
    # If pursuer: move toward opponent; if evader: move away from opponent.
    pref_vx, pref_vy = (tx, ty) if pursuer else (-tx, -ty)

    best_dxdy = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        # Base objective: pursuer wants smaller dist; evader wants larger dist.
        score = -dist if pursuer else dist

        # Obstacle/escape bias: prefer having more neighboring free cells.
        free_n = 0
        for ddx, ddy in dirs:
            if ddx == 0 and ddy == 0:
                continue
            ax, ay = nx + ddx, ny + ddy
            if valid(ax, ay):
                free_n += 1

        # Inertia bias: prefer continuing preferred direction (reduces zigzag).
        inertia = (dx * pref_vx + dy * pref_vy)
        score += 0.6 * free_n + 0.2 * inertia

        if best_score is None or (score > best_score):
            best_score = score
            best_dxdy = [dx, dy]

    return best_dxdy