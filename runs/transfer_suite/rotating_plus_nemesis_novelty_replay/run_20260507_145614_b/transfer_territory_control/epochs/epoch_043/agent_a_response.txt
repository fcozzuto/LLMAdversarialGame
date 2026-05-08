def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    resources = [tuple(p[:2]) for p in (observation.get("resources") or []) if p and len(p) >= 2]
    self_terr = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    start_idx = (observation["turn_index"] or 0) % len(dirs)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed_set = set(unclaimed)
    opp_list = list(opp_terr)
    un_list = unclaimed if unclaimed else (resources if resources else opp_list)

    def mindist(a, b_list):
        if not b_list:
            return 0
        ax, ay = a
        m = None
        for bx, by in b_list:
            d = abs(bx - ax) + abs(by - ay)
            if m is None or d < m:
                m = d
        return m if m is not None else 0

    best_move = (0, 0)
    best_score = None

    for i in range(len(dirs)):
        dx, dy = dirs[(start_idx + i) % len(dirs)]
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cell = (nx, ny)

        score = 0.0
        if cell in unclaimed_set:
            score += 8.0
        if cell in opp_terr:
            score += 10.0
        if cell in self_terr:
            score += 2.0

        d_un = mindist(cell, un_list)
        d_opp = abs(nx - ox) + abs(ny - oy)
        score += -0.35 * d_un + 0.05 * d_opp

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]