def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    frontier = []
    if self_terr:
        for x, y in unclaimed:
            for dx, dy in neigh8:
                if (x + dx, y + dy) in self_terr:
                    frontier.append((x, y))
                    break

    if frontier:
        target = min(frontier, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    elif unclaimed:
        target = min(unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    elif opp_terr:
        target = min(opp_terr, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    else:
        target = (w // 2, h // 2)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - target[0]) + abs(ny - target[1])

        if (nx, ny) in unclaimed:
            land = 2
        elif (nx, ny) in opp_terr:
            land = 1
        elif (nx, ny) in self_terr:
            land = 0
        else:
            land = -1

        cand = (dist, -land, abs(dx) + abs(dy))
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])

    return best[1] if best is not None else [0, 0]