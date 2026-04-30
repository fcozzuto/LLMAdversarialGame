def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    oppd = abs(sx - ox) + abs(sy - oy)
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_for_cell(x, y):
        if (x, y) in obstacles:
            return None
        if not inside(x, y):
            return None
        if resources:
            md = 10**9
            for rx, ry in resources:
                d = abs(rx - x) + abs(ry - y)
                if d < md:
                    md = d
            dist_resource = md
        else:
            dist_resource = man(x, y, w//2, h//2)
        dist_opp = man(x, y, ox, oy)
        # Greedy toward resources; mild avoidance/contesting near opponent
        score = dist_resource * 10 - dist_opp
        if oppd <= 2:
            score += dist_opp * 5  # keep away when close
        return score

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        s = best_for_cell(nx, ny)
        if s is None:
            continue
        # Tie-break deterministically toward resource direction, then toward staying
        res_dir = (0, 0)
        if resources:
            rx, ry = resources[0]
            for i in range(len(resources)):
                tx, ty = resources[i]
                if abs(tx - nx) + abs(ty - ny) < abs(rx - nx) + abs(ry - ny):
                    rx, ry = tx, ty
            res_dir = (0 if rx == nx else (1 if rx > nx else -1), 0 if ry == ny else (1 if ry > ny else -1))
        bias = (abs(dx - res_dir[0]) + abs(dy - res_dir[1]))*2 + (dx==0 and dy==0)*1
        candidates.append((s + bias, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]