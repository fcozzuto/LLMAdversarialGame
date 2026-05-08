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
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    oppT = to_set("opponent_territory")
    selfT = to_set("self_territory")
    inside = lambda x, y: 0 <= x < w and 0 <= y < h

    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Directly prefer resources if any
        if resources:
            if (nx, ny) in resources:
                val = 100
            else:
                tx, ty = min(resources, key=lambda p: (abs(p[0]-nx)+abs(p[1]-ny), p[0], p[1]))
                val = 30 - (abs(tx-nx) + abs(ty-ny))
        else:
            val = 0
            if (nx, ny) in unclaimed:
                val += 10
            if (nx, ny) in oppT:
                val += 24
            # Territory pressure: near unclaimed is better
            adj_un = 0
            for mx in (-1, 0, 1):
                for my in (-1, 0, 1):
                    ax, ay = nx + mx, ny + my
                    if (ax, ay) in unclaimed:
                        adj_un += 1
            val += adj_un * 1.5
            # Avoid moving closer to opponent if it doesn't expand
            d = abs(nx - ox) + abs(ny - oy)
            if (nx, ny) not in unclaimed and (nx, ny) not in oppT:
                val += (d * 0.3)

            # Slight bias to expand our blob
            if (nx, ny) in selfT:
                val += 0.5
            else:
                adj_self = 0
                for mx, my in neigh:
                    ax, ay = nx + mx, ny + my
                    if (ax, ay) in selfT:
                        adj_self += 1
                val += adj_self * 0.8

        cand.append((val, abs(ox-nx)+abs(oy-ny), dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][2]), int(cand[0][3])]