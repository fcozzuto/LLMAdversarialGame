def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]); sx = int(sx); sy = int(sy)
    ox, oy = observation.get("opponent_position", [w-1, h-1]); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                selfT.add((x, y))

    unT = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.append((x, y))

    def neigh4(x, y):
        return ((x+1,y), (x-1,y), (x,y+1), (x,y-1), (x+1,y+1), (x+1,y-1), (x-1,y+1), (x-1,y-1))

    frontier = []
    if selfT:
        for (x, y) in unT:
            for nx, ny in neigh4(x, y):
                if (nx, ny) in selfT:
                    frontier.append((x, y))
                    break

    targets = frontier if frontier else unT
    if not targets:
        return [0, 0]

    def man(a, b, c, d): return abs(a-c) + abs(b-d)
    best = None
    best_key = None
    for tx, ty in targets:
        if (tx, ty) in obstacles: 
            continue
        d_me = man(sx, sy, tx, ty)
        d_op = man(ox, oy, tx, ty)
        key = (d_me, -d_op, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        key = (d_target, -d_opp, dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]