def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]

    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []) if len(p) >= 2)
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Find nearest opponent cell and nearest unclaimed cell (bounded scan over provided lists).
    near_opp = None
    bestd = 10**9
    for x, y in opp_cells:
        d = cell_dist(sx, sy, x, y)
        if d < bestd:
            bestd = d
            near_opp = (x, y)
    near_un = None
    bestdu = 10**9
    for x, y in unclaimed:
        d = cell_dist(sx, sy, x, y)
        if d < bestdu:
            bestdu = d
            near_un = (x, y)

    tx, ty = (near_un if near_un is not None else (ox, oy))
    nx, ny = (tx, ty)

    best_move = (0, 0)
    best_score = -10**18

    # Deterministic tie-breaker order: dirs already fixed.
    for dx, dy in dirs:
        cx, cy = sx + dx, sy + dy
        if not inb(cx, cy) or (cx, cy) in obstacles:
            cx, cy = sx, sy
            dx, dy = 0, 0
        score = 0
        if (cx, cy) in opp_cells:
            score += 6  # flipping an opponent-owned cell is valuable
        if (cx, cy) in unclaimed:
            score += 3  # grabbing unclaimed expands territory
        if (cx, cy) in self_cells:
            score -= 0.5  # avoid wasting moves into already-owned cells

        # Move toward chosen target (unclaimed if exists else opponent)
        score += 0.25 * (-(cell_dist(cx, cy, nx, ny)))
        # Also bias toward opponent frontier if we have opponent cells
        if near_opp is not None:
            score += 0.15 * (-(cell_dist(cx, cy, near_opp[0], near_opp[1])))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]