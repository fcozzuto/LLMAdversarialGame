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

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def min_dist_to_opp(x, y):
        if not opp_set:
            return 999
        best = 999
        for ox, oy in opp_set:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
        return best

    def adj_has(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in s:
                    return True
        return False

    best_score = -10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        in_self = (nx, ny) in self_set
        in_opp = (nx, ny) in opp_set
        in_un = (nx, ny) in unclaimed
        adj_my = adj_has(nx, ny, self_set)
        adj_opp = adj_has(nx, ny, opp_set)
        md = min_dist_to_opp(nx, ny)

        score = 0
        if in_self:
            score += 2 + (0 if adj_opp else 1)
        elif in_un:
            score += (4 if adj_my else 1) + (0 if adj_opp else 3)
        elif in_opp:
            score += (7 if adj_my else 4) + (2 if not adj_opp else 0) + (md // 3)
        else:
            score += (1 if adj_my else 0)

        score += md * 0.05
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]