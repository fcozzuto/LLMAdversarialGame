def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    def to_set(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny):
                    yield nx, ny

    # Build frontier targets: unclaimed cells adjacent to opponent territory (strong expansion play)
    frontier = []
    if opp_t and unclaimed:
        for ox, oy in opp_t:
            for nx, ny in neigh8(ox, oy):
                if (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    frontier.append((nx, ny))
    if not frontier:
        frontier = list(unclaimed)

    # Fallback: if no unclaimed, try to move toward opponent territory cells
    if not frontier:
        frontier = list(opp_t) if opp_t else [(sx, sy)]

    # Deterministic tie-breaking: fixed order by (x,y), then manhattan distance
    frontier_sorted = sorted(frontier, key=lambda p: (p[0], p[1]))

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate closest target with a small deterministic computation
        best_dist = 10**9
        for t in frontier_sorted:
            d = manh((nx, ny), t)
            if d < best_dist:
                best_dist = d
                if best_dist == 0:
                    break

        # Immediate cell value: prefer unclaimed, then opponent territory (flipping), avoid giving up area (staying in own)
        if (nx, ny) in unclaimed:
            immediate = 140
        elif (nx, ny) in opp_t:
            immediate = 60
        elif (nx, ny) in self_t:
            immediate = 15
        else:
            immediate = 25

        # Keep away from edges/corners a bit (reduce getting trapped vs edge-claimer)
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen = 10
        center_bonus = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01

        # Total: maximize immediate + approach frontier; slight bias for staying/heading to center
        val = immediate + (40 - 6 * best_dist) + center_bonus - edge_pen

        # Deterministic tie-break by move order
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move