def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    self_cells = set(tuple(p) for p in observation.get("self_territory", []))
    opp_cells = set(tuple(p) for p in observation.get("opponent_territory", []))
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    w, h = observation["grid_width"], observation["grid_height"]
    best = -10**9
    best_move = [0, 0]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_score(cx, cy):
        if (cx, cy) in obstacles:
            return -10**6
        if (cx, cy) in self_cells:
            return 2
        if (cx, cy) in unclaimed:
            return 4 + (7 - min(w, h) + (manh(cx, cy, ox, oy) < manh(x, y, ox, oy)))
        if (cx, cy) in opp_cells:
            # Flipping on entry: prioritize capturing opponent cells while staying pressure-near.
            return 6 + (7 - min(w, h) + (manh(cx, cy, ox, oy) <= manh(x, y, ox, oy)))
        return 1

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            nx, ny = x, y
            dx, dy = 0, 0
        score = cell_score(nx, ny)
        # Extra shaping: prefer moves that reduce distance to opponent when not stepping into danger.
        d0 = manh(x, y, ox, oy)
        d1 = manh(nx, ny, ox, oy)
        score += 2 if d1 < d0 else 0
        score += 1 if d1 == d0 and ((nx, ny) in unclaimed or (nx, ny) in opp_cells) else 0
        # Avoid being adjacent to obstacles
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if in_bounds(tx, ty) and (tx, ty) in obstacles:
                    adj_obs += 1
        score -= 0.3 * adj_obs
        if score > best:
            best = score
            best_move = [dx, dy]

    return best_move