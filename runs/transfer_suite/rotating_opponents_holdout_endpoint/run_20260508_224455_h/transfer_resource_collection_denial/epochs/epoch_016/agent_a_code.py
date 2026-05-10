def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy

    # Denial-oriented target: pick resources farthest from opponent but relatively close to us.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -((rx + ry) & 7), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move step toward target with deterministic obstacle-avoidance.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        hit = 1 if (nx, ny) in obstacles else 0
        d = man(nx, ny, tx, ty)
        # Prefer unblocked and strictly reducing distance; otherwise minimal distance.
        cand.append((hit, d, abs(tx - nx) + abs(ty - ny), dx, dy))
    cand.sort()
    _, _, _, dx, dy = cand[0]
    if dx == 0 and dy == 0:
        return [0, 0]
    return [int(dx), int(dy)]