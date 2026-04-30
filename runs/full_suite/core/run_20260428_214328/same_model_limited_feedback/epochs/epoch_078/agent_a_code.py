def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    self_pos = observation["self_position"]; opp_pos = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    cx, cy = self_pos; ox, oy = opp_pos

    def cheb(a, b, c, d): 
        dx = a - c; dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate moves (deterministic order)
    moves = [(0,0), (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]

    valid = []
    for dx, dy in moves:
        nx = cx + dx; ny = cy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy))

    if not valid:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in valid:
            nx = cx + dx; ny = cy
            my_best = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer positions that are closer than opponent, and that reduce my distance to some resource
                val = (opd - myd) * 10 - myd
                if my_best is None or val > my_best:
                    my_best = val
            # Tie-break deterministically by favoring dx closer to direction to center
            dc = cheb(nx, ny, w//2, h//2)
            score = (my_best, -dc)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # No resources: go toward center while avoiding obstacles
    tx, ty = w//2, h//2
    best = None
    for dx, dy in valid:
        nx = cx + dx; ny = cy + dy
        score = -cheb(nx, ny, tx, ty)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]