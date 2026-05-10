def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    oppx, oppy = observation["opponent_position"]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    neigh4 = [(-1,0),(1,0),(0,-1),(0,1)]
    neigh8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if oppT:
        sx = sy = 0
        n = len(oppT)
        for px, py in oppT:
            sx += px; sy += py
        ocx, ocy = sx // n, sy // n
    else:
        ocx, ocy = oppx, oppy

    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in neigh8:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        adj_self = 0
        adj_opp = 0
        for ex, ey in neigh4:
            tx, ty = nx + ex, ny + ey
            if inb(tx, ty):
                if (tx, ty) in selfT:
                    adj_self += 1
                if (tx, ty) in oppT:
                    adj_opp += 1

        if (nx, ny) in selfT:
            v = 0.2 + 0.08 * adj_self - 0.06 * adj_opp
        elif (nx, ny) in unclaimed:
            v = 1.2 + 0.35 * adj_self - 0.25 * adj_opp
        elif (nx, ny) in oppT:
            v = 2.0 + 0.25 * adj_self - 0.1 * adj_opp
        else:
            v = 0.0

        man_to_opp = abs(nx - ocx) + abs(ny - ocy)
        v += -0.03 * man_to_opp
        if (nx, ny) in unclaimed:
            v += -0.01 * (abs(nx - oppx) + abs(ny - oppy))

        if v > bestv or (v == bestv and (dx, dy) < tuple(best_move)):
            bestv = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]