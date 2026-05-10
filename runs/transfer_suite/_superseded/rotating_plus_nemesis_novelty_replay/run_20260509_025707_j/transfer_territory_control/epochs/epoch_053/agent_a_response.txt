def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_dist_to_set(x, y, s):
        if not s:
            return 10**9
        md = 10**9
        for px, py in s:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    opp_dist_now = min_dist_to_set(sx, sy, opp_set)
    opp_adj_count = 0
    for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
        if (sx + dx, sy + dy) in opp_set:
            opp_adj_count += 1

    best = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        target = (nx, ny)

        gain = 0
        if target in opp_set:
            gain += 2000  # counterclaim
        elif target in unclaimed:
            gain += 80  # expand quickly
        elif target in self_set:
            gain += 15  # consolidation

        # Prefer approaching opponent while not getting stuck
        opp_dist = min_dist_to_set(nx, ny, opp_set)
        gain += (opp_dist_now - opp_dist) * 25

        # If stepping near opponent, boost
        adj = 0
        for ddx, ddy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            if (nx + ddx, ny + ddy) in opp_set:
                adj += 1
        gain += adj * 12

        # Discourage moving away from opponent
        gain -= max(0, opp_dist - opp_dist_now) * 8

        # Slightly encourage unclaimed over own territory when competitive
        if target in unclaimed:
            gain += 5

        if gain > best:
            best = gain
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]