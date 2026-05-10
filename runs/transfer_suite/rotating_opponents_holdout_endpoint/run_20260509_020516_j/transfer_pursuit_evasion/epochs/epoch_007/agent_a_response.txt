def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    def neighbors_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    if pursuer:
        best_move = (0, 0)
        best = None
        cur_d = d2(sx, sy, ox, oy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = d2(nx, ny, ox, oy)
            if nd == 0:
                return [dx, dy]
            # primary: minimize distance; secondary: maximize mobility after move
            # tertiary: prefer moves that make more progress when available
            progress = cur_d - nd
            key = (nd, -neighbors_count(nx, ny), -progress)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Evader: maximize distance; break ties by mobility and by moving away from opponent direction
    best_move = (0, 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = d2(nx, ny, ox, oy)
        away_x = 0 if ox == nx else (1 if nx > ox else -1)
        away_y = 0 if oy == ny else (1 if ny > oy else -1)
        away_bonus = (dx == away_x) + (dy == away_y) + (dx == 0 and away_x == 0) + (dy == 0 and away_y == 0)
        key = (-nd, -neighbors_count(nx, ny), -away_bonus)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]