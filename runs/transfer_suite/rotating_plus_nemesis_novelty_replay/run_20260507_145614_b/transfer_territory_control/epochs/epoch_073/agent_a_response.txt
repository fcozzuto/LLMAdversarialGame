def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h: obstacles.add((x, y))
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_terr if p and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_terr if p and len(p) >= 2)
    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h: yield nx, ny

    # Pick target: unclaimed adjacent to opponent territory; else nearest unclaimed; else move toward opponent.
    opp_front = set()
    for (x, y) in opp_set:
        for nx, ny in neigh8(x, y):
            if (nx, ny) not in obstacles and (nx, ny) not in opp_set: opp_front.add((nx, ny))
    best_targets = []
    if opp_front:
        for c in unclaimed:
            if c in opp_front: best_targets.append(c)
    targets = best_targets if best_targets else (unclaimed if unclaimed else [ (ox, oy) ])
    # Deterministic tie-breaker: distance then x then y
    tx, ty = min(targets, key=lambda c: (man(sx, sy, c[0], c[1]), c[0], c[1]))

    # Evaluate next move with local scoring (attack if entering opponent territory; otherwise expand into target; avoid obstacles).
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (None, -10**9)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): continue
        if (nx, ny) in obstacles:
            continue  # engine would keep us; we avoid to prevent repeated hits
        score = 0
        if (nx, ny) in opp_set:
            score += 500 + 2 * man(nx, ny, tx, ty)
        if (nx, ny) == (tx, ty):
            score += 300
        score += -man(nx, ny, tx, ty)
        # Prefer moves that increase frontier pressure on opponent
        if (nx, ny) not in self_set:
            near_opp = 0
            for ax, ay in neigh8(nx, ny):
                if (ax, ay) in opp_set: near_opp += 1
            score += 10 * near_opp
        # Mild preference for open area (avoid getting trapped near obstacles)
        wall = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in obstacles: wall += 1
        score -= 2 * wall
        if score > best[1] or (score == best[1] and (dx, dy) < best[0]):
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]