def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # quick adjacency map to reward moves that can potentially flip boundary
    def is_adj_to_opp_boundary(x, y):
        # if an unclaimed cell is next to opponent territory, capturing it denies them and can flip soon
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_terr:
                    return True
        return False

    # main target: nearest unclaimed, but if none, drift toward opponent territory front
    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda c: man(sx, sy, c[0], c[1]))
    else:
        # pick nearest cell that is adjacent to opponent territory
        candidates = []
        for (ox, oy) in opp_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: 
                        continue
                    nx, ny = ox + dx, oy + dy
                    if inb(nx, ny) and (nx, ny) not in obstacles:
                        candidates.append((nx, ny))
        if candidates:
            target = min(set(candidates), key=lambda c: man(sx, sy, c[0], c[1]))
        else:
            target = opp_pos

    best = -10**18
    best_move = [0, 0]
    tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        score = 0.0
        if cell in self_terr:
            score += 0.25
        if cell in unclaimed:
            score += 2.5
        if cell in opp_terr:
            score += 1.6  # flipping onto opponent territory is valuable if it happens
        if is_adj_to_opp_boundary(nx, ny):
            score += 0.9
        score += 0.02 * man(nx, ny, tx, ty) * (-1)  # closer to target is better
        # mild preference toward advancing overall rather than staying
        if dx == 0 and dy == 0:
            score -= 0.15
        # keep from oscillating into same cell repeatedly: slight push away if exact target
        if man(nx, ny, tx, ty) == 0:
            score += 0.2

        if score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]