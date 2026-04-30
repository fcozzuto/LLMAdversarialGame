def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    me = (sx, sy)
    op = (ox, oy)

    # If no visible resources, retreat from opponent while keeping toward center.
    if not resources:
        cx, cy = (w-1)//2, (h-1)//2
        best = None
        best_sc = -10**9
        for dx, dy in legal:
            nm = (sx+dx, sy+dy)
            sc = -dist(nm, op) - dist(nm, (cx, cy))
            if sc > best_sc:
                best_sc, best = sc, (dx, dy)
        return [best[0], best[1]]

    # Choose move that creates the biggest advantage on a contested resource.
    best = legal[0]
    best_sc = -10**9
    for dx, dy in legal:
        nm = (sx+dx, sy+dy)
        # Find target resource where our relative progress is best (we prefer smaller self_dist-opp_dist).
        best_gap = 10**9
        closest_for_me = 10**9
        for r in resources:
            sd = dist(nm, r)
            od = dist(op, r)
            gap = sd - od
            if gap < best_gap:
                best_gap = gap
            if sd < closest_for_me:
                closest_for_me = sd
        # Prefer moves that reduce our distance to a resource, and avoid giving the opponent too much proximity.
        # Also penalize getting too close to opponent to reduce contest swing.
        sc = -best_gap * 10 - closest_for_me
        sc -= max(0, 4 - dist(nm, op)) * 3
        # Mild bias to avoid edging against boundaries when tie.
        sc -= abs(nm[0] - (w-1)/2) * 0.01 + abs(nm[1] - (h-1)/2) * 0.01
        if sc > best_sc:
            best_sc, best = sc, (dx, dy)

    return [int(best[0]), int(best[1])]