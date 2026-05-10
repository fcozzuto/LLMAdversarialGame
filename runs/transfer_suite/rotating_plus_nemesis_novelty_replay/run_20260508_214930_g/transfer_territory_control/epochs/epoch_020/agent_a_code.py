def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def edge_bias(nx, ny):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return - (abs(nx - cx) + abs(ny - cy)) * 0.01

    best_dx, best_dy, best_score = 0, 0, -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        target = (nx, ny)
        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)

        if target in self_t:
            score = 1.0 + 0.5 * a_self
        elif target in opp_t:
            score = 8.0 + 2.2 * a_self + 0.8 * a_opp
        elif target in unclaimed:
            score = 4.5 + 2.0 * a_self - 1.2 * a_opp
        else:
            score = 0.2 + 0.3 * a_self - 0.2 * a_opp

        score += edge_bias(nx, ny)

        # deterministic tie-break
        key = (-(abs(dx) + abs(dy)), dx, dy)
        best_key = (-(abs(best_dx) + abs(best_dy)), best_dx, best_dy)
        if score > best_score or (score == best_score and key > best_key):
            best_score, best_dx, best_dy = score, dx, dy

    return [int(best_dx), int(best_dy)]