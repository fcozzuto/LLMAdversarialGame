def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neigh4(x, y):
        return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    def neigh8(x, y):
        return [(x+dx,y+dy) for dx in (-1,0,1) for dy in (-1,0,1) if not (dx==0 and dy==0)]
    def man(x1, y1, x2, y2): return abs(x1-x2)+abs(y1-y2)

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    targets = []
    if unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)

    # Choose a "goal" deterministically: nearest unclaimed; otherwise nearest opponent territory; else center.
    if targets:
        if unclaimed:
            goal = min(targets, key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))
        else:
            goal = min(targets, key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))
    else:
        goal = (w // 2, h // 2)

    # Heuristic: prefer expanding the frontier safely and avoid being exposed to opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy, nx, ny in valid:
        val = 0

        # Base: move toward goal
        val += -man(nx, ny, goal[0], goal[1])

        # Cell type
        if (nx, ny) in unclaimed:
            val += 12
        if (nx, ny) in opp_terr:
            # flipping is advantageous, but be careful if it creates an exposed pocket
            val += 10

        # Frontier alignment: reward adjacency to own territory (easier to defend)
        adj_self = sum((a, b) in self_terr for a, b in neigh4(nx, ny))
        adj_opp = sum((a, b) in opp_terr for a, b in neigh4(nx, ny))
        val += 4 * adj_self
        val -= 3 * adj_opp

        # Exposure: if move is surrounded by opponent in 8-neighborhood, penalize
        opp_neigh8 = sum((a, b) in opp_terr for a, b in neigh8(nx, ny))
        val -= 1.2 * opp_neigh8

        # "Pressure" toward uncertain area: prefer moves closer to unclaimed if available
        if unclaimed:
            # Use a deterministic small sample of candidate targets near the goal direction
            # (avoid heavy search)
            sample = []
            gx, gy = goal
            for tx, ty in targets[:min(20, len(targets))]:
                sample.append((abs(tx-gx)+abs(ty-gy), tx, ty))
            sample.sort()
            k = min(5, len(sample))
            if k:
                closest = min(sample[:k], key=lambda t: man(nx, ny, t[1], t[2]))
                val += 3.0 / (1 + man(nx, ny, closest[1], closest[2]))

        # Prefer diagonal when equally good (deterministic tie-break)
        val += 0.01 * (1 if dx != 0 and dy != 0 else 0)
        val += 0.001 * (dx + 2*dy)  # deterministic bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]