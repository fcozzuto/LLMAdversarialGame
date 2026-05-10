def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    oppx, oppy = observation.get("opponent_position", (0, 0))
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    ucell = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    obset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dxdy = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obset:
            continue

        cell_bonus = 0
        if (nx, ny) in ucell:
            cell_bonus = 3
        elif (nx, ny) in oset:
            cell_bonus = 2
        elif (nx, ny) in uset:
            cell_bonus = 1
        else:
            cell_bonus = 0

        center_term = dist(nx, ny, cx, cy)  # prefer edges (larger)
        opp_term = dist(nx, ny, oppx, oppy)  # prefer farther from center-fighter

        val = cell_bonus * 10 + 0.02 * center_term + 0.01 * opp_term
        if val > best_val:
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy