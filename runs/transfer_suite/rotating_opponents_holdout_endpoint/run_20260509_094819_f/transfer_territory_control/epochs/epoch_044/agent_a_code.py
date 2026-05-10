def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def nearest_to_self(x, y):
        if not selfT:
            return abs(x - sx) + abs(y - sy)
        best = 10**9
        for (a, b) in selfT:
            d = abs(x - a) + abs(y - b)
            if d < best:
                best = d
        return best

    def adj_self(x, y):
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ax, y + ay) in selfT:
                return True
        return False

    def adj_opp(x, y):
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ax, y + ay) in oppT:
                return True
        return False

    opp_central_bias = abs(sx - ox) + abs(sy - oy)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**17
        else:
            val = 0
            if (nx, ny) in oppT:
                val += 220  # stealing/flip priority
            elif (nx, ny) in uncla:
                val += 55   # expand into unclaimed
            if (nx, ny) in selfT:
                val -= 5    # avoid cycling inside owned area
            if adj_self(nx, ny):
                val += 25   # keep expansion connected
            else:
                val -= 12   # discourage lone forays
            if adj_opp(nx, ny):
                val += 18   # press opponent boundary
            val += -2 * nearest_to_self(nx, ny)
            # gentle pull toward opponent to keep pressure (deterministic)
            val += -0.35 * (abs(nx - ox) + abs(ny - oy)) + 0.02 * opp_central_bias

        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]