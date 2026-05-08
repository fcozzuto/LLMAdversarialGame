def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obst = set((p[0], p[1]) for p in obstacles)

    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursuer" in self_role) or ("pursur" in self_role)

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def wall_pen(nx, ny):
        # mild penalty for hugging walls/corners (but stay within bounds already)
        return (nx == 0) + (nx == w-1) + (ny == 0) + (ny == h-1)

    def obst_adj_pen(nx, ny):
        c = 0
        for ax, ay in [(1,0),(-1,0),(0,1),(0,-1)]:
            x, y = nx + ax, ny + ay
            if 0 <= x < w and 0 <= y < h and (x, y) in obst:
                c += 1
        return c

    # Heuristic target: pursuer minimizes distance; evader maximizes distance while avoiding being cornered.
    best = None
    for dx, dy, nx, ny in legal:
        d = abs(nx - ox) + abs(ny - oy)
        oap = obst_adj_pen(nx, ny)
        wp = wall_pen(nx, ny)
        if is_pursuer:
            # Prefer moves that reduce distance; avoid obstacle adjacency; discourage wall hugging.
            score = (-d * 100) + (-oap * 5) + (-wp * 2) + (-(abs(nx - sx) + abs(ny - sy)) * 0)
        else:
            # Evader wants to increase distance, avoid obstacle adjacency, and avoid cornering.
            score = (d * 100) + (-oap * 6) + (-wp * 6) + (-(abs(nx - sx) + abs(ny - sy)) * 0)

        # Deterministic tie-breaker by move order and exact position
        key = (score, -nx, -ny, dx, dy) if best is None else (score, -nx, -ny, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]