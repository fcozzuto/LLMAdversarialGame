def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_in(x, y, S):
        c = 0
        for dx, dy in dirs4:
            if (x + dx, y + dy) in S:
                c += 1
        return c

    target = None
    frontier_unclaimed = []
    for uc in unclaimed:
        x, y = uc
        if adj_in(x, y, opp_terr) > 0:
            frontier_unclaimed.append(uc)
    candidates_targets = frontier_unclaimed if frontier_unclaimed else list(unclaimed)
    if candidates_targets:
        target = min(candidates_targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[1], p[0]))

    def min_dist_to_opponent(x, y):
        return abs(ox - x) + abs(oy - y)

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        is_self = cell in self_terr
        is_opp = cell in opp_terr
        is_unc = cell in unclaimed
        adj_own = adj_in(nx, ny, self_terr)
        adj_opp = adj_in(nx, ny, opp_terr)
        dist_opp = min_dist_to_opponent(nx, ny)
        dist_t = abs(nx - target[0]) + abs(ny - target[1]) if target else 0

        score = 0.0
        if is_unc:
            score += 2.6
        if is_opp:
            score += 4.2
        if is_self:
            score -= 0.3
        score += 0.35 * adj_own
        score -= 0.25 * adj_opp
        score += -0.06 * dist_opp
        if target:
            score += -0.08 * dist_t

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]