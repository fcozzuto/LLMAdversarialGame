def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = {(p[0], p[1]) for p in observation.get("obstacles") or []}
    self_set = {(p[0], p[1]) for p in observation.get("self_territory") or []}
    opp_set = {(p[0], p[1]) for p in observation.get("opponent_territory") or []}
    unclaimed = {(p[0], p[1]) for p in observation.get("unclaimed_cells") or []}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    opp_list = list(opp_set)
    un_list = list(unclaimed)
    focus = opp_list if opp_list else un_list

    def nearest_dist_from(pos, arr):
        if not arr:
            return 99
        x, y = pos
        best = 99
        for tx, ty in arr:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx = 0 if nx == sx else (1 if nx > sx else -1)
            dy = 0 if ny == sy else (1 if ny > sy else -1)

        in_opp = (nx, ny) in opp_set
        in_un = (nx, ny) in unclaimed
        in_self = (nx, ny) in self_set

        d_opp = nearest_dist_from((nx, ny), opp_list)
        d_un = nearest_dist_from((nx, ny), un_list)

        score = 0
        if in_opp:
            score += 6.0
        if in_un:
            score += 2.0
        if in_self:
            score -= 0.2

        if behind:
            score += (4.0 / (1 + d_opp)) if opp_list else (1.5 / (1 + d_un))
        else:
            score += (3.5 / (1 + d_opp)) if opp_list else (2.0 / (1 + d_un))

        if dx == 0 and dy == 0:
            score -= 0.3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]