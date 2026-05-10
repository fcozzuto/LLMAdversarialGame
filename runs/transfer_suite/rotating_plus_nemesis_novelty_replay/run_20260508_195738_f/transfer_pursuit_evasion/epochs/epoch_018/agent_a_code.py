def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    # Pursuit if we are pursuer; otherwise treat as evader maximizing distance
    i_am_pursuer = ("purs" in self_role) or ("evader" not in self_role and "purs" not in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    # If evader, we avoid that corner by targeting the opposite side; if pursuer, we cut off.
    if i_am_pursuer:
        tx, ty = (ox + far_corner[0]) // 2, (oy + far_corner[1]) // 2
    else:
        # flee to the corner farthest from opponent, but don't step into obstacles
        flee_corner = max(corners, key=lambda c: -abs(c[0] - ox) - abs(c[1] - oy))
        tx, ty = (flee_corner[0] + ox) // 2, (flee_corner[1] + oy) // 2

    tx, ty = clamp(tx, 0, w - 1), clamp(ty, 0, h - 1)

    best = None
    best_score = None
    # Also try to keep line pressure against opponent by preferring moves that reduce distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_opp = dist2(nx, ny, ox, oy)
        d_to_tgt = dist2(nx, ny, tx, ty)

        # Obstacle proximity penalty: avoid squares with more blocked neighbors
        neigh_blocked = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if (not (0 <= ax < w and 0 <= ay < h)) or ((ax, ay) in obstacles):
                neigh_blocked += 1

        # Interception: pursuer wants small dist2 to intercept target, also reduce opp distance.
        # Evader wants to increase opp distance while still moving toward flee target.
        if i_am_pursuer:
            score = (d_to_tgt * 3) + (d_to_opp * 1) + (neigh_blocked * 5)
            better = (best_score is None) or (score < best_score)
        else:
            score = (d_to_tgt * 1) - (d_to_opp * 3) + (neigh_blocked * 5)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best