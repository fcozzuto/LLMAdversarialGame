def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_list = list(opp_t)
    def min_opp_dist(x, y):
        if not opp_list:
            return 99
        dmin = 99
        for ox, oy in opp_list:
            d = abs(ox - x) + abs(oy - y)
            if d < dmin:
                dmin = d
        return dmin

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    self_count = int(observation.get("self_territory_count", len(self_t)) or 0)
    opp_count = int(observation.get("opponent_territory_count", len(opp_t)) or 0)
    leading = self_count >= opp_count

    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        val = 0
        if (nx, ny) in self_t:
            val += 0.5 if leading else 0.25
        elif (nx, ny) in opp_t:
            val += 18.0 if leading else 22.0
            val += 0.5 * (8 - min_opp_dist(nx, ny))
        elif (nx, ny) in unclaimed:
            val += 6.0 if edge_dist(nx, ny) <= 2 else 4.0
            val += 0.25 * (8 - min_opp_dist(nx, ny))
        else:
            val -= 1.0  # unknown/covered by neither (rare)
        # frontier incentive: move toward unclaimed neighbors and away from obstacles
        frontier = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in unclaimed:
                frontier += 1
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                frontier -= 0.15
        val += 1.2 * frontier
        # keep pressure toward opponent by preferring decreasing manhattan distance
        val += (leading and -0.2) * min_opp_dist(nx, ny)
        if val > bestv:
            bestv = val
            best_move = [dx if (nx, ny) != (sx, sy) else 0, dy if (nx, ny) != (sx, sy) else 0]
    return [int(best_move[0]), int(best_move[1])]