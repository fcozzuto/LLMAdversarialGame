def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources", []) or [])]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal_cell(x, y):
        return inside(x, y) and (x, y) not in obst and (x, y) != (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my_legal = [(dx, dy) for dx, dy in moves if legal_cell(sx + dx, sy + dy)]
    if not my_legal: return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        ax = ax - bx; ay = ay - by
        return abs(ax) if abs(ax) >= abs(ay) else abs(ay)

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    if resources:
        opp_target = min(resources, key=lambda r: cheb(opp_pos, r))
        my_target = min(resources, key=lambda r: cheb(my_pos, r))
    else:
        opp_target = None
        my_target = None

    # Predict opponent greedy next cells toward opp_target
    threat_cells = set()
    if opp_target is not None:
        opp_legal = []
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if legal_cell(nx, ny):
                opp_legal.append((dx, dy, nx, ny))
        if opp_legal:
            best = min(cheb((nx, ny), opp_target) for _, _, nx, ny in opp_legal)
            for _, _, nx, ny in opp_legal:
                if cheb((nx, ny), opp_target) == best:
                    threat_cells.add((nx, ny))

    best = None
    best_val = -10**9
    for dx, dy in my_legal:
        nx, ny = sx + dx, sy + dy
        pos = (nx, ny)

        val = 0
        # Strongly avoid stepping into opponent's immediate cell (already filtered) and favor grabbing resources
        if resources and pos in set(resources):
            val += 1000

        if my_target is not None:
            my_d = cheb(pos, my_target)
            val += (8 - my_d)
        if opp_target is not None:
            my_to_opp_target = cheb(pos, opp_target)
            opp_d_now = cheb(opp_pos, opp_target)
            val += 0.6 * (opp_d_now - my_to_opp_target)  # if I get closer than opp, gain

        # Blocking: occupy squares opponent is likely to choose next
        if pos in threat_cells:
            val += 12

        # Soft repulsion from being too close to opponent unless beneficial
        d_opp = cheb(pos, opp_pos)
        val -= 0.2 * d_opp

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]