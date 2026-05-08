def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Prefer frontier: unclaimed adjacent to our territory
    frontier = []
    for x, y in my:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in un and (nx, ny) not in obstacles:
                frontier.append((nx, ny))
    if not frontier:
        frontier = list(un)

    # Deterministic tie-break: sort by (score, x, y)
    def best_target_score(x, y):
        # closer is better; also slightly avoid opponent proximity
        du = abs(x - cx) + abs(y - cy)
        do = abs(x - ox) + abs(y - oy)
        return du * 0.9 + do * 0.1

    frontier.sort(key=lambda p: (best_target_score(p[0], p[1]), p[1], p[0]))

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate immediate move with territory-intent heuristic
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        val = 0
        if (nx, ny) in opp:
            val += 1200  # flipping on entry
        elif (nx, ny) in un:
            val += 250
        elif (nx, ny) in my:
            val += 5
        else:
            val -= 30

        # Move towards best frontier tile
        tx, ty = frontier[0] if frontier else (int(round(cx)), int(round(cy)))
        dist = abs(nx - tx) + abs(ny - ty)
        val += 60 - dist * 8

        # Mild preference to keep distance from opponent early (territory_center_claim)
        val += -abs(nx - ox) - abs(ny - oy) * 0.4

        # Encourage expanding to frontier-adjacent cells
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay) and (ax, ay) in un:
                val += 18

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]