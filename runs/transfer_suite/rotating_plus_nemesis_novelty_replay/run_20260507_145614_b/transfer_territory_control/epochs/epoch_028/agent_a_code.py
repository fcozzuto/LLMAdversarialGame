def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = {tuple(p) for p in observation.get("obstacles", []) if p and len(p) >= 2}
    self_t = {tuple(p) for p in observation.get("self_territory", []) if p and len(p) >= 2}
    opp_t = {tuple(p) for p in observation.get("opponent_territory", []) if p and len(p) >= 2}
    resources = {tuple(p) for p in observation.get("resources", []) if p and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d0 = abs(sx - ox) + abs(sy - oy)
        d1 = abs(nx - ox) + abs(ny - oy)

        val = 0
        val += (d0 - d1) * 10  # prefer closer to opponent
        if (nx, ny) in resources:
            val += 200
        if (nx, ny) in opp_t:
            val += 150  # step into opponent territory if possible
        if (nx, ny) in self_t:
            val += 20   # keep within our territory
        if (nx, ny) not in self_t and d1 > 0:
            val -= 5     # slight penalty for leaving territory

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move