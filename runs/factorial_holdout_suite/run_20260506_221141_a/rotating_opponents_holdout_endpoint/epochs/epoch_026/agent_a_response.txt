def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res_list = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    res_set = set(res_list)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        immediate = 1 if (nx, ny) in res_set else 0
        if immediate:
            return [dx, dy]

        # Tactical targeting: prefer resources where we are closer; if opponent is closer,
        # bias toward resources that deny/avoid their advantage and reduce "contested" moves.
        local_best = -10**9
        for r in res_list:
            ds = cheb((nx, ny), r)
            do = cheb((ox, oy), r)
            # If opponent is closer, make this target less attractive but still allow progress.
            # Also discourage stepping toward highly contested (small ds+do) zones.
            contested = 1.0 / (ds + do + 1)
            val = (do - ds) * 2.0 - ds * 0.6 - contested * 3.0
            if val > local_best:
                local_best = val

        # Tiny symmetry-break: prefer moves that increase distance from opponent when equally good.
        opp_dist = cheb((nx, ny), (ox, oy))
        score = local_best + opp_dist * 0.01

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]