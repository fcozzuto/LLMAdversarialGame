def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh4 = [(-1,0),(1,0),(0,-1),(0,1)]
    neigh8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def adj_to_opp(cx, cy):
        for dx, dy in neigh4:
            tx, ty = cx + dx, cy + dy
            if inb(tx, ty) and (tx, ty) in oppT:
                return True
        return False

    # Opponent "center" for deterministic pressure (if empty, use position)
    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px; sy += py
        ocx, ocy = sx // n, sy // n
    else:
        ocx, ocy = ox, oy

    # Candidate moves (including staying); engine will reject invalid by staying
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):  # invalid -> would be kept in place, so score as stay
            nx, ny = x, y
            dx, dy = 0, 0
        if (nx, ny) in obstacles:
            nx, ny = x, y
            dx, dy = 0, 0

        # Base value: reward claiming / flipping; reward edge steals more
        if (nx, ny) in unclaimed:
            v = 2.0
        elif (nx, ny) in oppT:
            v = 6.0
        elif (nx, ny) in selfT:
            v = 0.2
        else:
            # could be unknown/obstacle; keep minimal
            v = -1.0

        if (nx, ny) in unclaimed or (nx, ny) in oppT:
            if adj_to_opp(nx, ny):
                v += 4.0  # target opponent edges
            # Prefer moving closer to opponent overall
            v += (8 - man(nx, ny, ocx, ocy)) * 0.08

        # Avoid obstacle adjacency traps
        adj_obs = 0
        for ax, ay in neigh4:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        v -= adj_obs * 0.6

        # Mild preference for diagonal/forward progression toward opponent center
        v += -0.02 * (man(nx, ny, ocx, ocy) - man(x, y, ocx, ocy))

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best