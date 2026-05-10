def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles)

    role = observation.get("self_role", "pursuer")
    pursuer = (role != "evader")

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obst:
                continue
            d = dist2(nx, ny, ox, oy)
            # pursuer wants minimize distance; evader wants maximize distance
            base = -d if pursuer else d
            # slight preference for moving (reduce boundary-sticking)
            move_bonus = -0.01 * (dx == 0 and dy == 0)
            # corner bias to reduce escape loops for evader; for pursuer, to cut lines to far corner
            cornerx = 0 if (nx < w / 2) else (w - 1)
            cornery = 0 if (ny < h / 2) else (h - 1)
            corner_dist = abs(nx - cornerx) + abs(ny - cornery)
            corner_term = (-0.001 * corner_dist) if pursuer else (0.001 * corner_dist)
            # deterministic tie-break by (base, move_bonus, -corner_term) later
            score = base + move_bonus + corner_term
            candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]
    # Choose best score; tie-break deterministically by dx, dy ordering
    candidates.sort(key=lambda t: (t[0], -t[1], -t[2]), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]