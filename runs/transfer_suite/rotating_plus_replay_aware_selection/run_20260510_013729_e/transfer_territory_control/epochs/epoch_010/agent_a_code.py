def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
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

    if not unclaimed and not resources:
        return [0, 0]

    def nearest_unclaimed_dist(px, py):
        if unclaimed:
            return min(abs(cx - px) + abs(cy - py) for (cx, cy) in unclaimed)
        return 10**9

    cur_du = nearest_unclaimed_dist(x, y)
    best = (-(10**18), 0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in resources:
            sc += 120
        if (nx, ny) in unclaimed:
            sc += 70
        if (nx, ny) in self_ter:
            sc += 10
        if (nx, ny) in opp_ter:
            sc -= 90

        du = nearest_unclaimed_dist(nx, ny)
        sc += (cur_du - du) * 12  # closer to unclaimed is good

        # Prefer expanding frontiers near our territory
        if (nx, ny) in unclaimed:
            neigh_our = 0
            for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in self_ter:
                    neigh_our += 1
            sc += neigh_our * 4

        # Avoid stepping into opponent territory unless it strongly accelerates unclaimed capture
        if (nx, ny) in opp_ter:
            improvement = cur_du - du
            if improvement < 2:
                sc -= 120
            else:
                sc += improvement * 8  # limited, but allows tactical flip

        # Keep pressure without sacrificing too much: slightly favor moves that reduce distance to opponent
        sc += (abs(x - ox) + abs(y - oy) - (abs(nx - ox) + abs(ny - oy))) * 1.5

        # Small deterministic tie-breaker: lexicographic on (dx,dy)
        cand = (sc, -dx, -dy)
        if sc > best[0]:
            best = (sc, dx, dy)

    return [best[1], best[2]]