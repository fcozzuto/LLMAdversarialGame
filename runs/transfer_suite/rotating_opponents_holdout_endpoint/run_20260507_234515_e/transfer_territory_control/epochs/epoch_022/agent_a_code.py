def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or [0, 0])
    ox, oy = map(int, observation.get("opponent_position") or [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    self_ter = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_ter = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    tx = 0 if ox > (w - 1) / 2 else (w - 1)
    ty = 0 if oy > (h - 1) / 2 else (h - 1)

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to_opp = dist(nx, ny, ox, oy)
            d_to_target = dist(nx, ny, tx, ty)
            if (nx, ny) in unclaimed:
                base = 200
            elif (nx, ny) in opp_ter:
                base = 120  # capture by entry (flipping enabled)
            elif (nx, ny) in self_ter:
                base = 35
            else:
                base = 0
            # prefer progress toward target while staying away from opponent
            s = base + (2.2 * d_to_opp) - (1.6 * d_to_target)
            # mild bias to avoid getting stuck near opponent territory edge
            if (nx, ny) in opp_ter:
                s += 0.3 * d_to_opp
            # deterministic tie-break: lexicographic on move
            if s > best_score or (s == best_score and (dx, dy) < best):
                best_score = s
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]