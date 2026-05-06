def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # Keep moving toward opponent to discourage, otherwise drift to nearest edge.
        edges = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(edges, key=lambda t: dist(sx, sy, t[0], t[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    opp_close = dist(sx, sy, ox, oy) <= 3
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0.0
        for rx, ry in resources:
            dme = dist(nx, ny, rx, ry)
            dop = dist(ox, oy, rx, ry)
            # Prefer resources where we are closer; increase weight when contesting.
            lead = dop - dme
            val += (1.5 if opp_close else 1.0) * (lead * 2.0) / (1.0 + dme)
            # Strong pull to the nearest resource overall.
            val += 0.6 / (1.0 + dme)
            # Slight penalty if opponent is much closer and will likely take it.
            if lead < 0:
                val -= (1.2 if opp_close else 0.7) * (-lead) / (1.0 + dme)
        # Mild preference for staying away from blocked-adjacent traps (use free-neighbor count)
        free_n = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in blocked:
                free_n += 1
        val += 0.05 * free_n
        if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]