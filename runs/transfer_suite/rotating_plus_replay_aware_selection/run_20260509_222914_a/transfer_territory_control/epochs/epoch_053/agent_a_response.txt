def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_ter = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_ter = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = [(int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []) if inside(int(x), int(y))]

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_near = set()
    for x, y in opp_ter:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                opp_near.add((nx, ny))

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    candidates = unclaimed if unclaimed else []
    if not candidates:
        candidates = list(opp_near) + list(self_ter)
        candidates = [c for c in candidates if inside(c[0], c[1])]

    best_goal = None
    best_score = None
    for gx, gy in candidates:
        g = (gx, gy)
        d_self = dist((sx, sy), g)
        d_opp = dist((ox, oy), g)
        adj_opp = 1 if g in opp_near else 0
        in_self = 1 if g in self_ter else 0
        in_opp = 1 if g in opp_ter else 0
        # Prefer unclaimed farther from opponent, but allow entry into opponent if close.
        score = d_self + 3 * adj_opp + (8 if in_self else 0) + (0 if in_opp == 0 else max(0, 6 - d_opp))
        if best_score is None or score < best_score or (score == best_score and (gx, gy) < best_goal):
            best_score, best_goal = score, g

    gx, gy = best_goal if best_goal is not None else (sx, sy)
    move_options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ng = (nx, ny)
        val = dist(ng, (gx, gy))
        # Small bias to expand territory: avoid stepping into opponent if not closer goal.
        if ng in opp_ter:
            val += 2
        # Keep away from obstacles-adjacent only when equally good (stable tie-break).
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]