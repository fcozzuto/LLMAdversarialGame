def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles", []) or []))
    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory", []) or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory", []) or []))
    unC = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    turn = int(observation.get("turn_index", 0) or 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    target_set = unC if unC else oppT

    def nearest_dist(x, y, S):
        if not S:
            return 10**9
        md = 10**9
        for px, py in S:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    best = None
    best_val = -10**18

    base_priority = turn & 1
    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            val = 0
            if (nx, ny) in oppT:
                val += 9
            elif (nx, ny) in unC:
                val += 6
            elif (nx, ny) in selfT:
                val += 2
            else:
                val += 1
            val -= nearest_dist(nx, ny, target_set)
            # Prefer consolidating near our border; small deterministic bias by move index
            if base_priority == (i & 1):
                val += 0.01
        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val and best is not None:
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best