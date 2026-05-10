def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((p[0], p[1]))

    self_cells = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_cells.add((p[0], p[1]))

    opp_cells = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_cells.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 1000
        if (nx, ny) in self_cells:
            val += 50
        if (nx, ny) in opp_cells:
            val += 200

        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += -d_self
        val += -2 * d_opp

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val:
            if [dx, dy] < best:
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best