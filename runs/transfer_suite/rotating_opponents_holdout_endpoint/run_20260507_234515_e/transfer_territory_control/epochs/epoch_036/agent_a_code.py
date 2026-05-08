def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    oppT = to_set("opponent_territory")
    selfT = to_set("self_territory")

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = moves[0]
    best_score = -10**18

    res_list = list(resources)
    near_res = None
    if res_list:
        near_res = min(abs(sx-x) + abs(sy-y) for x, y in res_list)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in resources:
            score += 200
        if (nx, ny) in unclaimed:
            score += 60
        if (nx, ny) in oppT:
            score += 40
        if (nx, ny) in selfT:
            score += 15
        dO = abs(nx - ox) + abs(ny - oy)
        score += dO * 2

        if res_list:
            dR = 10**9
            for x, y in res_list:
                d = abs(nx - x) + abs(ny - y)
                if d < dR: dR = d
            score += (20 - dR) * 2  # closer to resource is better

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move