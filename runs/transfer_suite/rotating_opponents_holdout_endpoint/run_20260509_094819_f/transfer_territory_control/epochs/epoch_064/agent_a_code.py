def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) == 2)
    my_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2]
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Pick a deterministic target
    candidates = []
    if unclaimed:
        for ux, uy in unclaimed:
            if (ux, uy) in obstacles:
                continue
            candidates.append((man(sx, sy, ux, uy), ux, uy))
        if candidates:
            candidates.sort()
            tx, ty = candidates[0][1], candidates[0][2]
        else:
            tx, ty = ox, oy
    else:
        tx, ty = ox, oy

    # Score moves: avoid obstacles; prefer our territory; then get closer to target; discourage proximity to opponent a bit
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in my_t:
            sc += 200
        sc += -man(nx, ny, tx, ty)
        sc += 0.1 * man(nx, ny, ox, oy)
        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]