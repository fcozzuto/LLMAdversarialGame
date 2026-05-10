def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if len(p) >= 2)
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if len(p) >= 2)
    unT = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if len(p) >= 2]
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    frontier = []
    for x, y in selfT:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in selfT and (nx, ny) not in opT:
                frontier.append((nx, ny))
    frontier = [p for p in frontier if p in set(unT)]
    un_set = set(unT)

    if not frontier:
        candidates = [p for p in un_set if (abs(p[0]-sx)+abs(p[1]-sy)) <= 3]
        if not candidates:
            candidates = unT
    else:
        candidates = frontier

    best = (sx, sy)
    best_val = -10**9
    for tx, ty in candidates:
        if (tx, ty) == (sx, sy): continue
        if not inb(tx, ty): continue
        # Prefer easy expansion from our edge; avoid moving into opponent-adjacent chokepoints.
        adj_to_opp = 0
        for dx, dy in neigh:
            if (tx + dx, ty + dy) in opT: adj_to_opp += 1
        edge_bonus = 3 if (tx, ty) in frontier else 1
        dist_self = abs(tx - sx) + abs(ty - sy)
        dist_opp = abs(tx - ox) + abs(ty - oy)
        val = 10 * edge_bonus + dist_opp - 2 * dist_self - 6 * adj_to_opp
        # If opponent controls nearby, slightly prefer cells that are farther from them.
        if adj_to_opp >= 2: val -= 8
        if val > best_val:
            best_val = val
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If immediate diagonal/step is blocked by obstacle, fall back deterministically to axis move.
    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny):
        options = []
        if inb(sx + dx, sy): options.append((dx, 0))
        if inb(sx, sy + dy): options.append((0, dy))
        if inb(sx, sy): options.append((0, 0))
        if options:
            # deterministic pick: prefer reducing both distances if possible
            options.sort(key=lambda m: (abs((sx+m[0])-tx)+abs((sy+m[1])-ty), m[0]!=0))
            return [options[0][0], options[0][1]]
        return [0, 0]
    return [dx, dy]