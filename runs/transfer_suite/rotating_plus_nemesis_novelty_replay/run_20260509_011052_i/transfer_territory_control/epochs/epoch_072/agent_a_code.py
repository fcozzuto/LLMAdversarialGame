def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells", []) or []
    un_set = []
    for p in unclaimed:
        try:
            un_set.append((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # fallback if no unclaimed provided
    if not un_set:
        d = abs(ox - sx) + abs(oy - sy)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = (abs(ox - nx) + abs(oy - ny)) - 0.001 * d
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # deterministic list for nearest computation
    un_list = un_set

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        du = 10**9
        if un_list:
            for ux, uy in un_list:
                t = abs(ux - nx) + abs(uy - ny)
                if t < du:
                    du = t
        dist_opp = abs(ox - nx) + abs(oy - ny)
        gain_un = 0
        for ux, uy in un_list:
            if ux == nx and uy == ny:
                gain_un = 1000
                break
        v = gain_un + (200 - du) + 0.1 * dist_opp
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]