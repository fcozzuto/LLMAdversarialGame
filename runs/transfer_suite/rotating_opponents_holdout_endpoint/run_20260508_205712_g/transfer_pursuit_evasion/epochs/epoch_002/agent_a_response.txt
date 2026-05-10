def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(a[0]), int(a[1])) for a in obstacles if len(a) >= 2}
    self_role = (observation.get("self_role", "") or "").lower()

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("catch" in self_role)
    if pursuer:
        # Chase: minimize squared distance; if equal, prefer moves that reduce opponent's escape options.
        best_move = [0, 0]
        best_val = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # "Wall pressure": prefer moving closer to edges to limit opponent's room.
            edge_bonus = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            # Smaller edge_bonus means closer to wall/obstacle region; use it to break ties deterministically.
            val = (d, edge_bonus, dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    # Evader: run away; maximize distance from pursuer, but don't step into walls/obstacles.
    # Also avoid moving into squares where pursuer has many immediate escape captures (proxy: its adjacency freedom).
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Proxy danger: how many legal moves the pursuer would have from the opponent position.
        legal = 0
        for pdx, pdy in deltas:
            tx, ty = ox + pdx, oy + pdy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs_set:
                legal += 1
        # Prefer higher distance; if tie, prefer reducing pursuer mobility.
        val = (-d, legal, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move