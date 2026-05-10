def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def obstacle_proximity(nx, ny):
        # small deterministic tie-break: prefer farther from obstacles
        if not obs:
            return 0
        md = 10**9
        for x, y in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < md:
                md = d
        return md

    best_move = (0, 0)
    if is_pursuer:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            towards_x = 0
            if ox > sx:
                towards_x = 1 if nx > sx else (-1 if nx < sx else 0)
            elif ox < sx:
                towards_x = 1 if nx < sx else (-1 if nx > sx else 0)
            towards_y = 0
            if oy > sy:
                towards_y = 1 if ny > sy else (-1 if ny < sy else 0)
            elif oy < sy:
                towards_y = 1 if ny < sy else (-1 if ny > sy else 0)
            # minimize distance; then maximize progress; then avoid obstacles
            key = (dist, -towards_x - towards_y, -obstacle_proximity(nx, ny), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            away_x = 0
            if ox > sx:
                away_x = 1 if nx < sx else (-1 if nx > sx else 0)
            elif ox < sx:
                away_x = 1 if nx > sx else (-1 if nx < sx else 0)
            away_y = 0
            if oy > sy:
                away_y = 1 if ny < sy else (-1 if ny > sy else 0)
            elif oy < sy:
                away_y = 1 if ny > sy else (-1 if ny < sy else 0)
            # maximize distance; then prefer moving away; then keep away from obstacles
            key = (-dist, -(away_x + away_y), -obstacle_proximity(nx, ny), -dx, -dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]