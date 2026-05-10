def choose_move(observation):
    w = observation.get("grid_width", 0); h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_ter = set(map(tuple, observation.get("self_territory", [])))
    opp_ter = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h

    best_dx, best_dy, best_sc = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in resources:
            sc += 30
        if (nx, ny) in unclaimed:
            sc += 45
        if (nx, ny) in self_ter:
            sc += 8
        if (nx, ny) in opp_ter:
            sc -= 120
        # Prefer moving toward unclaimed and slightly toward the opponent while avoiding their territory
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_to_border = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1)]:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in unclaimed:
                dist_to_border += 1
        sc += 10 * dist_to_border
        sc += (18 - dist_opp)  # larger is better
        sc -= 2 * (dx == 0 and dy == 0)
        if sc > best_sc:
            best_sc = sc; best_dx, best_dy = dx, dy
    return [best_dx, best_dy]