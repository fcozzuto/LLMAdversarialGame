def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    # Determine whether we are pursuer (default to pursuer if ambiguous)
    i_am_pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if ("evader" in self_role) or ("evade" in self_role):
        i_am_pursuer = False

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dy in dys for dx in dxs]  # deterministic order

    best_move = (0, 0)
    if i_am_pursuer:
        # Chase: minimize squared distance to opponent, prefer safer (not blocked)
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if best_d is None or d < best_d:
                best_d = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # Evade: maximize distance from pursuer; tie-break by preferring moves that are not in extreme corners
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Penalize being near corners to reduce getting trapped (deterministic tie-break)
            corner_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            score = (d, -corner_pen, -abs(w // 2 - nx), -abs(h // 2 - ny))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]