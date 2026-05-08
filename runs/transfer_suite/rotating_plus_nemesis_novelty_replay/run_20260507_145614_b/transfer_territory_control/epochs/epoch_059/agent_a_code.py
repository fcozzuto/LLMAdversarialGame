def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2 and 0 <= p[0] < w and 0 <= p[1] < h:
            obstacles.add((p[0], p[1]))
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    self_cells = set((p[0], p[1]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2 and inb(p[0], p[1]))
    opp_cells = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2 and inb(p[0], p[1]))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2 and inb(p[0], p[1]):
            unclaimed.add((p[0], p[1]))
    if not unclaimed:
        return [0, 0]

    # Candidates: prioritize unclaimed adjacent to our territory (frontier). If none, take a far-from-opponent cell.
    nbrs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    frontier = set()
    if self_cells:
        for x, y in self_cells:
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    candidates = list(frontier) if frontier else list(unclaimed)

    def man(a, b, c, d): return abs(a - c) + abs(b - d)
    best = None; best_key = None
    for tx, ty in candidates:
        du = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Edge-claimer tendency: take interior/away from opponent and avoid being too easy to contest.
        k = (-(do - du), du, -tx, -ty)  # minimize ( -(do-du) ) == maximize (do-du), tie-breakers
        if best_key is None or k < best_key:
            best_key = k; best = (tx, ty)
    tx, ty = best

    # Choose deterministic 1-step move (including diagonals) that minimizes distance to target.
    best_move = (0, 0); best_md = None; best_s = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                mx, my = sx, sy
            else:
                mx, my = sx + dx, sy + dy
            if not inb(mx, my):
                continue
            md = man(mx, my, tx, ty)
            # Prefer entering opponent territory (flipping), otherwise prefer unclaimed.
            s = (1 if (mx, my) in opp_cells else 0) + (0.5 if (mx, my) in unclaimed else 0)
            k = (md, -s, dx, dy)
            if best_md is None or k < (best_md, best_s, best_move[0], best_move[1]):
                best_md = md; best_s = s; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]