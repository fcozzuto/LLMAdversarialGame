def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(a,b): return 0 <= a < w and 0 <= b < h

    if opp_ter:
        tgt = min(opp_ter, key=lambda p: abs(p[0]-x)+abs(p[1]-y))
    else:
        tgt = (ox, oy)

    frontier = set()
    for ux, uy in unclaimed:
        for dx, dy in dirs:
            if (ux+dx, uy+dy) in self_ter:
                frontier.add((ux, uy))
                break

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x+dx, y+dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        cell = (nx, ny)
        if cell in opp_ter:
            score = 100000
        elif cell in self_ter:
            score = 5000
        elif cell in frontier:
            score = 600 + 2 * (w+h)
        elif cell in unclaimed:
            score = 200
        else:
            score = 0
        dist_t = abs(nx - tgt[0]) + abs(ny - tgt[1])
        score += -dist_t
        score += -2 * (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score > best_score or (score == best_score and (dx,dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]