def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))

    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = adj8 + [(0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def has_adj(cell_set, x, y):
        for dx, dy in adj8:
            if (x + dx, y + dy) in cell_set:
                return True
        return False

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        is_un = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_t
        is_opp = (nx, ny) in opp_t

        adj_self = 1 if has_adj(self_t, nx, ny) else 0
        adj_opp = 1 if has_adj(opp_t, nx, ny) else 0

        sc = 0
        sc += 6 if is_un else 2 if is_self else 0
        sc += -7 if is_opp else 0
        sc += 4 * adj_self
        sc += -3 * adj_opp

        # Prefer distancing from opponent to reduce their sweep effectiveness
        sc += (dist(nx, ny, ox, oy) ** 0.5) * 0.2

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]