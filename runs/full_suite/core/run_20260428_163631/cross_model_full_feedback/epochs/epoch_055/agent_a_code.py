def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Deterministic tie-break: fixed ordering by move index
    best_i = 0
    best_val = -10**18

    for i, (dx, dy, nx, ny) in enumerate(legal):
        my = (nx, ny)
        opp = (ox, oy)
        val = 0
        # Prefer being ahead of opponent for valuable resources
        if resources:
            for r in resources:
                dm = man(my, r)
                do = man(opp, r)
                ahead = do - dm  # positive if we are closer
                # Encourage capturing (ahead), discourage being behind
                val += (ahead * 10) - (dm * 1)
        else:
            val += -man(my, opp) * 0.5

        # Avoid collisions / getting too close to opponent when resources exist
        dmo = man(my, opp)
        val += (dmo * 0.5)
        if resources:
            # If opponent is adjacent, prioritize distancing slightly
            if dmo <= 1:
                val -= 12

        # Slight preference to reduce distance to the single closest resource
        if resources:
            dmin = min(man(my, r) for r in resources)
            val -= dmin * 2

        # If we are about to be stuck behind obstacles, still choose safest move
        if val > best_val:
            best_val = val
            best_i = i

    dx, dy, _, _ = legal[best_i]
    return [int(dx), int(dy)]