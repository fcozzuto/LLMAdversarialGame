def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def toset(lst):
        s = set()
        for p in lst or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_terr = toset(observation.get("self_territory") or [])
    opp_terr = toset(observation.get("opponent_territory") or [])
    unclaimed = toset(observation.get("unclaimed_cells") or [])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    my_neighbors_cache = None

    def adj8(x, y):
        cnt_un = 0
        cnt_opp = 0
        cnt_my = 0
        for dx, dy in ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                if (nx, ny) in unclaimed:
                    cnt_un += 1
                if (nx, ny) in opp_terr:
                    cnt_opp += 1
                if (nx, ny) in self_terr:
                    cnt_my += 1
        return cnt_un, cnt_my, cnt_opp

    def cell_score(x, y):
        if (x, y) in obstacles or not (0 <= x < w and 0 <= y < h):
            return -10**9
        base = 0
        if (x, y) in self_terr:
            base += 2
        if (x, y) in unclaimed:
            base += 4
        if (x, y) in opp_terr:
            base += 6  # flipping helps
        cnt_un, cnt_my, cnt_opp = adj8(x, y)
        base += cnt_un * 1.5
        base += cnt_my * 1.0
        base -= cnt_opp * 0.2
        # Prefer pushing away from opponent to avoid being swapped back repeatedly
        base += -0.03 * (abs(x - ox) + abs(y - oy))
        return base

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc > best[0]:
            best = (sc, dx, dy)

    return [int(best[1]), int(best[2])]