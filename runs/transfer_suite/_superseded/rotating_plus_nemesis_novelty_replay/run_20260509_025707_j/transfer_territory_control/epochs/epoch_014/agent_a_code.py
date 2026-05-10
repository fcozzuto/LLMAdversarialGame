def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    opp_cells = set((p[0], p[1]) for p in observation.get("opponent_territory", []))
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_to_set(x, y, S):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                return True
        return False

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in unclaimed and adj_to_set(nx, ny, opp_cells):
            v += 2000
        elif (nx, ny) in unclaimed:
            v += 400 if adj_to_set(nx, ny, opp_cells) else 200
        elif (nx, ny) in opp_cells:
            v -= 1000
        if adj_to_set(nx, ny, opp_cells):
            v += 120
        d = abs(nx - ox) + abs(ny - oy)
        v += -d
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is not None:
        return best
    return [0, 0]