def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_cell(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        s = 0
        if (nx, ny) in opp_ter:
            s += 120  # strong flip pressure
        elif (nx, ny) in unclaimed:
            s += 70  # claim potential
        elif (nx, ny) in self_ter:
            s += 20  # extend/keep
        else:
            s += 5
        # center pressure (opponent tends to center-claim)
        s += 25 - (abs(nx - cx) + abs(ny - cy))
        # frontier bonus: if move makes us adjacent to opponent territory or unclaimed
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if not inb(xx, yy) or (xx, yy) in obstacles:
                    continue
                if (xx, yy) in opp_ter:
                    s += 18
                elif (xx, yy) in unclaimed:
                    s += 10
        return s

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]