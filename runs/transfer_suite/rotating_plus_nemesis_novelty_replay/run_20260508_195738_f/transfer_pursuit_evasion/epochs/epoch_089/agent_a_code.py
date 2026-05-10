def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role) or ("pursuer" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        # Extra penalty if standing adjacent to obstacle (helps avoid trap corners)
        adj_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (nx + dx, ny + dy) in obstacles:
                        adj_obs += 1
        dist = abs(nx - ox) + abs(ny - oy)
        if self_is_pursuer:
            # Pursuer: minimize distance to opponent, avoid adjacency to obstacles
            return -(dist * 10 + adj_obs)
        # Evader: maximize distance, but also avoid moving onto/near obstacles
        return dist * 10 - adj_obs

    best = None
    bestv = -10**18
    # Deterministic tie-breaking: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_move(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]