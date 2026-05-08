def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or (role == "evader")
    is_pursuer = ("purs" in role) or (role == "pursuer") or ("chaser" in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    # Deterministic corner bias for evader if far moves tie
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_target():
        # choose corner farthest from opponent; tie by fixed corner order
        best = corners[0]
        bestd = -1
        for c in corners:
            cx, cy = c
            d = (cx - ox) * (cx - ox) + (cy - oy) * (cy - oy)
            if d > bestd:
                bestd, best = d, c
        return best

    tx, ty = corner_target()

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dsq = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # pursuer: minimize distance; evader: maximize distance
        # if role unclear, infer pursuer if closer on average (simple fallback)
        if is_pursuer:
            primary = -dsq
        elif is_evader:
            primary = dsq
        else:
            primary = -dsq if ((sx + sy) <= (ox + oy)) else dsq

        # small obstacle/boundary smoothing: avoid going toward blocked cells by counting free neighbors
        free_n = 0
        for adx, ady in deltas:
            ax, ay = nx + adx, ny + ady
            if valid(ax, ay):
                free_n += 1

        # corner pull for evader
        corner_d = (nx - tx) * (nx - tx) + (ny - ty) * 1 + (ny - ty) * 0  # deterministic
        # Replace with proper corner distance:
        corner_d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)

        # Combine
        score = primary
        score += 0.01 * free_n
        if is_evader or (not is_pursuer and not is_evader):
            score += 0.001 * (-corner_d) if is_evader else 0.0

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]