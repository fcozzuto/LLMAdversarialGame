def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def neigh_legal_count(x, y):
        c = 0
        for dx, dy in moves:
            if legal(x + dx, y + dy):
                c += 1
        return c

    # No resources: drift to safer center while avoiding obstacles.
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (10**9, -10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            trap = neigh_legal_count(nx, ny)
            val = (d, -trap, 0 if (dx, dy) == (0, 0) else 1, (dx, dy)[0] * 3 + (dy, dy)[1])
            if val < best:
                best = val
                ans = [dx, dy]
        return ans if best[0] != 10**9 else [0, 0]

    # Choose a resource where we are relatively closer than the opponent.
    best_resource = None
    best_key = (10**9, 10**9, 10**9, 10**9)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        rel = sd - od  # negative means we are closer
        # Prefer: (1) more advantage, then (2) closer self, then (3) deterministic tie by position.
        key = (rel, sd, -od, rx + ry * 9)
        if key < best_key:
            best_key = key
            best_resource = (rx, ry)

    tx, ty = best_resource

    # Move one step toward target, but avoid obstacles and low-mobility cells.
    best_move = None
    best_score = (-10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_now = cheb(sx, sy, tx, ty)
        d_next = cheb(nx, ny, tx, ty)
        if d_next > d_now + 0:  # don't deliberately increase distance unless unavoidable
            continue
        # If equal distance, prefer moves that still progress (e.g., reducing to a better diagonal/axis alignment)
        opp_next_d = cheb(ox + dx, oy + dy, tx, ty) if in_bounds(ox + dx, oy + dy) else cheb(ox, oy, tx, ty)
        trap = neigh_legal_count(nx, ny)
        score = (-(d_next), (trap), -(opp_next_d))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]