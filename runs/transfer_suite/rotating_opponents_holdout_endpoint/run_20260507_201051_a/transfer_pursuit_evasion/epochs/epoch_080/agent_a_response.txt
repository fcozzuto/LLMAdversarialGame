def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)

    # Deterministic tie-break: lexicographic on (dx,dy)
    best = None
    best_score = None

    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; emulate deterministically

        d = abs(nx - ox) + abs(ny - oy)

        if is_pursuer:
            # Chase: primarily minimize Manhattan distance; add slight preference to move toward center.
            center_bias = -0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            score = -d + center_bias
        else:
            # Evade: primarily maximize distance; add slight bias toward corners far from opponent.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max((abs(cx - ox) + abs(cy - oy), i) for i, (cx, cy) in enumerate(corners))[1]
            cx, cy = corners[far_corner]
            corner_bias = 0.005 * (abs(nx - cx) * -1)  # prefer getting closer to far corner
            score = d + corner_bias

        if best_score is None or (score > best_score):
            best_score = score
            best = [dx, dy]

    return best