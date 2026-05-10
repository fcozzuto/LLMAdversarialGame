def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def opp_nearest_dist(nx, ny):
        if oppT:
            best = 10**9
            for px, py in oppT:
                d = md(nx, ny, px, py)
                if d < best:
                    best = d
            return best
        return md(nx, ny, ox, oy)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in selfT:
            base = 10
        elif (nx, ny) in unclaimed:
            base = 100
        elif (nx, ny) in oppT:
            base = 70
        else:
            base = 5

        # Encourage expansion near our frontier; discourage walking into opponent proximity.
        adj_own = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1)]:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in selfT:
                adj_own += 1

        dopp = opp_nearest_dist(nx, ny)
        # Strongly prefer safer steps when we can't expand.
        danger = 0
        if dipp := (dopp if dopp < 6 else 6):
            danger = (6 - dipp) * 20

        val = base + adj_own * 12 + dopp * 3 - danger

        # Deterministic tie-break: prefer moves with larger dx, then larger dy, then staying last.
        if val > best_val or (val == best_val and (dx, dy, -1 if dx==0 and dy==0 else 0) > (best_move[0], best_move[1], -1 if best_move[0]==0 and best_move[1]==0 else 0)):
            best_val = val
            best_move = [dx, dy]

    return best_move