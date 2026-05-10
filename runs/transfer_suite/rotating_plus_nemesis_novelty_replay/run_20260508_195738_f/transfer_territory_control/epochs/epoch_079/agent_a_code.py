def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    un_list = list(unclaimed)

    def min_manh_to(points, nx, ny):
        if not points:
            return 10**9
        best = 10**9
        for px, py in points:
            d = abs(px - nx) + abs(py - ny)
            if d < best:
                best = d
        return best

    def adj_to_set(nx, ny, s):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (nx + ddx, ny + ddy) in s:
                    return True
        return False

    # Determine which unclaimed likely fronts near our territory (edge claim)
    frontier_un = []
    if un_list:
        for ux, uy in un_list:
            if adj_to_set(ux, uy, selft):
                frontier_un.append((ux, uy))
    target_un_list = frontier_un if frontier_un else un_list

    # Prefer approaching opponent edges while expanding into frontiers
    best = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0

        in_opp = (nx, ny) in opp
        in_un = (nx, ny) in unclaimed
        in_self = (nx, ny) in selft

        if in_opp:
            score += 1600  # strong incentive to flip
        elif in_un:
            score += 260
        elif in_self:
            score += 40

        if opp and adj_to_set(nx, ny, opp):
            score += 220

        # Obstacle-safe and edge-seeking: reduce distance to opponent and frontier
        score -= 18 * min_manh_to(opp_list, nx, ny)
        if target_un_list:
            score -= 10 * min_manh_to(target_un_list, nx, ny)

        # Keep from drifting away from opponent edge when close
        score += 8 * (1 if opp_list and min_manh_to(opp_list, nx, ny) <= min_manh_to(opp_list, x, y) else 0)

        # Deterministic tie-break: prefer moves with smaller dx/dy magnitude then lexicographic
        if score > best:
            best = score
            best_move = [dx, dy]
        elif score == best:
            cur = (abs(dx) + abs(dy), dx, dy)
            prev = (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])
            if cur < prev:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]