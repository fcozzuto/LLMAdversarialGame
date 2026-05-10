def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_ter = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_ter.add((x, y))

    opp_ter = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_ter.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    adj_dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def adj_count(cell, ter):
        x, y = cell
        c = 0
        for dx, dy in adj_dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in ter:
                c += 1
        return c

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def eval_cell(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return -10**9
        if (nx, ny) in self_ter:
            gain = 0
        elif (nx, ny) in opp_ter:
            gain = 3
        elif (nx, ny) in unclaimed:
            gain = 2
        else:
            gain = 0
        neigh_self = adj_count((nx, ny), self_ter)
        neigh_opp = adj_count((nx, ny), opp_ter)
        if gain == 0:
            gain = -1
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # prefer pushing towards opponent while staying connected to our territory
        return (gain * 10) + (neigh_self * 2) + (neigh_opp * 1) - dist_to_opp * 0.05

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = eval_cell(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]