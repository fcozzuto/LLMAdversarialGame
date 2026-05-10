def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    oppx, oppy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    un = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        gain = 0
        if (nx, ny) in opp:
            gain += 3
        elif (nx, ny) in un:
            gain += 2
        # prefer expanding perimeter: move into cells adjacent to opponent/unclaimed
        adj = [(nx + ddx, ny + ddy) for ddx in (-1, 0, 1) for ddy in (-1, 0, 1) if not (ddx == 0 and ddy == 0)]
        adj_opp = sum(1 for ax, ay in adj if (ax, ay) in opp)
        adj_un = sum(1 for ax, ay in adj if (ax, ay) in un)
        gain += 0.4 * adj_un + 0.8 * adj_opp
        # strategic positioning
        dist_self = abs(nx - sx) + abs(ny - sy)
        dist_opp = abs(nx - oppx) + abs(ny - oppy)
        dist_center = abs(nx - cx) + abs(ny - cy)
        score = (gain * 10) + (-0.2 * dist_self) + (-0.03 * dist_opp) + (-0.01 * dist_center)
        # deterministic tie-breaker
        tieb = (dx, dy)
        if score > best_score or (score == best_score and (tieb < best)):
            best_score = score
            best = tieb

    return [best[0], best[1]]