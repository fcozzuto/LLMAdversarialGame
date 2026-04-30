def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def d2(ax, ay, bx, by): 
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    opp_next = set()
    for ddx, ddy in deltas:
        nx, ny = ox + ddx, oy + ddy
        if inb(nx, ny) and (nx, ny) not in obst:
            opp_next.add((nx, ny))

    # Choose target resource: maximize advantage over opponent.
    if resources:
        best = None
        for rx, ry in resources:
            myd = d2(x, y, rx, ry)
            od = d2(ox, oy, rx, ry)
            # Higher means we are better positioned to reach it soon.
            score = (od - myd) * 10 - myd * 0.001 - od * 0.0001
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = w // 2, h // 2

    # Pick move that heads to target while avoiding opponent pressure.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Distance to target after move
        myd = d2(nx, ny, tx, ty)

        # Opponent pressure after move
        od = d2(nx, ny, ox, oy)
        # Chebyshev proximity (diagonal reach)
        cheb = max(abs(nx - ox), abs(ny - oy))

        # Strong penalty for landing where opponent can step immediately
        opp_land = 1 if (nx, ny) in opp_next else 0

        # Avoid being adjacent (small but consistent)
        adj_pen = 1 if cheb <= 1 else 0

        val = (myd, -od, opp_land, adj_pen, (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]