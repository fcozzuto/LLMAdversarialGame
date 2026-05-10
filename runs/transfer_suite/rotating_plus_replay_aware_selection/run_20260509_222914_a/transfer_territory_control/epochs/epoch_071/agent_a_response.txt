def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in observation.get("self_territory") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in observation.get("opponent_territory") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in observation.get("obstacles") or [] if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in self_ter:
            score += 3
        elif (nx, ny) in unclaimed:
            score += 7
        elif (nx, ny) in opp_ter:
            score += 6

        # Prefer expansion toward center and toward opponent when raiding/contesting
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.01
        score += center_bias

        if (nx, ny) in unclaimed:
            score += 0.06 * md(ox, oy, nx, ny)  # keep pressure away from opponent core to claim space
        elif (nx, ny) in opp_ter:
            score += 0.1 * (16 - md(ox, oy, nx, ny))  # closer raids get priority

        # Avoid stepping next to large opponent territory wall unless taking unclaimed
        adj_opp = 0
        for ax, ay in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in opp_ter:
                adj_opp += 1
        if (nx, ny) in self_ter or (nx, ny) in unclaimed:
            score -= 0.35 * adj_opp

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]