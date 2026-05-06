def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    # If no resources: drift to increase separation from opponent (deterministic)
    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            # prefer moves that keep self farther from opponent (chebyshev)
            d = cheb(nx, ny, ox, oy)
            # tie-break by lexicographically smallest (dx,dy)
            v = d * 1000 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18

    # Heuristic:
    # - Prefer moves that make self closest to some resource relative to opponent
    # - Also prefer lowering own best distance and raising opponent's best distance
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        self_best_d = 10**9
        opp_best_d = 10**9
        lead_best = -10**9

        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)

            if sd < self_best_d:
                self_best_d = sd
            if od < opp_best_d:
                opp_best_d = od

            # lead if self gets closer than opponent to this resource
            lead = (od - sd)
            if lead > lead_best:
                lead_best = lead

        # Main objective: win resource races; secondary: reduce distance to reachable resources
        v = lead_best * 50 + (opp_best_d - self_best_d) * 10 - self_best_d

        # Tertiary tie-break: avoid stepping "toward" opponent too much if all else equal
        opp_sep = cheb(nx, ny, ox, oy)
        v = v + opp_sep * 0.1

        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]