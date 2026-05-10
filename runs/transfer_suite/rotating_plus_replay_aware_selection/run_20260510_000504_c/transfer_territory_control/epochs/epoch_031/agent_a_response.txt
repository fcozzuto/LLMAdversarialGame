def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def is_blocked(x, y): return (x, y) in obstacles

    def neigh8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def dist_to_opp_border(x, y):
        # Prefer moves that approach opponent-claimed area without committing to isolated cells
        best = 10**9
        for ox, oy in opp_terr:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
        return best if opp_terr else 0

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or is_blocked(nx, ny):
            continue
        # Base gain: occupy/unclaim/opponent territory
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 12
        elif (nx, ny) in opp_terr:
            gain += 18  # flipping is enabled on entry
        elif (nx, ny) in self_terr:
            gain += 1
        # Expansion: how many unclaimed neighbors we can immediately secure vicinity
        exp = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in unclaimed and (ax, ay) not in obstacles:
                exp += 1
        gain += 3 * exp
        # Safety: avoid stepping into cells that have very low freedom (surrounded by obstacles/opponent/self)
        free = 0
        for ax, ay in neigh8(nx, ny):
            if not is_blocked(ax, ay):
                free += 1
        gain += free  # higher freedom tends to reduce being trapped
        # Opponent pressure: slight bias toward opponent when close
        opp_border = dist_to_opp_border(nx, ny)
        if opp_border:
            gain += max(0, 7 - opp_border)
        # Deterministic tie-break: prefer diagonals, then toward increasing x,y for our corner (0,0)
        tb = (1 if dx != 0 and dy != 0 else 0) * 0.01 + (nx * 0.0001) + (ny * 0.00005)
        score = gain + tb
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]