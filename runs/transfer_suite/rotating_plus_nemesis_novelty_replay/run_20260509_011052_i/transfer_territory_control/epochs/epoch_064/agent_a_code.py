def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    center = (w - 1) / 2.0, (h - 1) / 2.0
    def dist_center(x, y):
        return abs(x - center[0]) + abs(y - center[1])

    def min_dist_to_opp(x, y):
        if opp_terr:
            best = 10**9
            for px, py in opp_terr:
                d = abs(px - x) + abs(py - y)
                if d < best:
                    best = d
            return best
        return abs(ox - x) + abs(oy - y)

    # Prefer grabbing unclaimed, expanding frontier, and keeping distance from opponent
    best_move = [0, 0]
    best = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            # flipping gives high immediate swing; still consider risk of immediate counter-attack
            base = 200.0
        elif (nx, ny) in unclaimed:
            base = 40.0
        elif (nx, ny) in self_terr:
            base = 5.0
        else:
            base = 10.0  # unknown/edge cells

        # Frontier expansion: count how many adjacent unclaimed cells we'd touch
        adj_unclaimed = 0
        adj_self = 0
        adj_opp = 0
        for ddx, ddy in dirs4:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in unclaimed:
                adj_unclaimed += 1
            if (ax, ay) in self_terr:
                adj_self += 1
            if (ax, ay) in opp_terr:
                adj_opp += 1

        dc0 = dist_center(sx, sy)
        dc1 = dist_center(nx, ny)
        toward_center = (dc0 - dc1)  # positive if closer

        dopp = min_dist_to_opp(nx, ny)
        risk = -0.8 * max(0, 3 - dopp) - 0.2 * adj_opp

        score = base + 8.0 * adj_unclaimed + 1.5 * adj_self + 3.0 * toward_center + risk

        # Deterministic tie-break: prefer staying closer to center, then lower lexicographic move
        if score > best or (score == best and (dist_center(nx, ny), dx, dy) < (dist_center(best_move[0] + sx, best_move[1] + sy), best_move[0], best_move[1])):
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]