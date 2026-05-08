def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role)
    if not self_is_pursuer and (("purs" in opponent_role) or ("hunter" in opponent_role) or ("chaser" in opponent_role)):
        self_is_pursuer = False

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Precompute a simple "wall pressure" using local obstacle count
    def local_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    c += 1
        return c

    best = None
    best_score = None

    base_dx = 1 if ox > sx else (-1 if ox < sx else 0)
    base_dy = 1 if oy > sy else (-1 if oy < sy else 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy  # engine keeps in place on invalid move
        dist = abs(nx - ox) + abs(ny - oy)
        self_dist = abs(sx - ox) + abs(sy - oy)
        ddelta = self_dist - dist  # positive means closer
        obstacle_pressure = local_block(nx, ny)

        score = 0.0
        if self_is_pursuer:
            score = 10.0 * ddelta - 0.25 * obstacle_pressure
            # Encourage aligning movement directly towards opponent
            score += 0.08 if (dx == base_dx or dx == 0) and (dy == base_dy or dy == 0) else 0.0
            better = (best_score is None) or (score > best_score + 1e-12)
        else:
            score = 10.0 * (-ddelta) - 0.35 * obstacle_pressure
            # Encourage moving away from opponent; favor corners deterministically
            corner_x = 0 if nx <= w // 2 else w - 1
            corner_y = 0 if ny <= h // 2 else h - 1
            corner_score = abs(corner_x - ox) + abs(corner_y - oy)
            score += 0.01 * corner_score
            better = (best_score is None) or (score > best_score + 1e-12)

        if better:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]